import struct
import socket
import urllib
import random
import btencode
from itertools import chain
from constants import UDP_CONN_ID
from twisted.web.client import getPage
from twisted.internet import defer, reactor
from twisted.internet.protocol import DatagramProtocol

actions = {'connect': 0, 'announce': 1, 'scrape': 2, 'error': 3}
events = {'none': 0, 'completed': 1, 'started': 2, 'stopped': 3}

class UDPTracker(DatagramProtocol):

    def __init__(self, factory, host, port):
        self.factory = factory
        self.host = host
        self.port = port
        self.connect_trans_id = self.generate_32bit()
        self.key = self.generate_32bit()
        self.connected = False
        self.deferred = defer.Deferred()

    @defer.inlineCallbacks
    def announce(self, torrent):
        self.torrent = torrent
        host = yield reactor.resolve(self.host, timeout=(1, 3))
        self.host = host
        reactor.listenUDP(torrent.port, self)
        peers = yield self.deferred
        defer.returnValue(peers)

    def startProtocol(self):
        """Connect so we can only speak to one peer. Then send out the initial
        connection packet."""

        self.transport.connect(self.host, self.port)
        self.transport.write(struct.pack('!QII', UDP_CONN_ID,
                                    actions['connect'], self.connect_trans_id))
        self.timeout = reactor.callLater(5, self.timed_out)

    def timed_out(self):
        self.transport.loseConnection()

    def datagramReceived(self, datagram, addr):
        self.timeout.reset(5)
        if not self.connected:
            assert len(datagram) >= 16
            action, trans_id, conn_id = struct.unpack('!IIQ', datagram)
            assert action == 0
            assert self.connect_trans_id == trans_id
            self.connect_id = conn_id
            self.trans_id = self.generate_32bit()
            self.transport.write(self._make_announce_pack(actions['announce'],
                                                            events['started']))
            self.connected = True
        else:
            size = len(datagram)
            assert size >= 20
            action, trans_id = struct.unpack_from('!II', datagram)
            assert action == 1
            assert trans_id == self.trans_id
            datagram = datagram[8:]
            self.peers(datagram)
            self.timeout.cancel()
            self.transport.loseConnection()

    def peers(self, raw_data):
        # first 8 bytes is number of seeders and leechers - ignore
        peers_raw = raw_data[8:]

        #break into 6 byte chunks - 4 for ip 2 for port
        peers = (peers_raw[i:i+6] for i in range(0, len(peers_raw), 6))
        hosts_ports = [(socket.inet_ntoa(peer[0:4]),
                        struct.unpack('!H', peer[4:6])[0])
                        for peer in peers if len(peer) == 6]

        self.deferred.callback(hosts_ports)


    def _make_announce_pack(self, action, event):
        return struct.pack('!QII20s20sQQQIIIiH', self.connect_id, action,
                                    self.trans_id, self.torrent.info_hash,
                                    self.factory.client.client_id,
                                    self.torrent.downloaded, self.torrent.left,
                                    self.torrent.uploaded, event, 0, self.key,
                                    -1, self.torrent.port)

    @staticmethod
    def generate_32bit():
        m = 4294967295
        return random.randint(0, m)

class HTTPTracker(object):

    def __init__(self, factory, *args):
        self.factory = factory

    @defer.inlineCallbacks
    def announce(self, torrent):
        url = self._build_url(torrent, 'started')
        response = yield getPage(url, timeout=5)
        defer.returnValue(self._parse_response(response))

    def _parse_response(self, response):

        tracker_dict = btencode.btdecode(response)
        if 'failure reason' in tracker_dict:
            raise AnnounceError('''failure reason key in tracker response\
                                    %s:''' % tracker_dict['failure reason'])

        peers_raw = tracker_dict['peers']
        if isinstance(peers_raw, dict):
            raise AnnounceError('peers as dictionary model not implemented')

        #break into 6 byte chunks - 4 for ip 2 for port
        peers = (peers_raw[i:i+6] for i in range(0, len(peers_raw), 6))
        hosts_ports = [(socket.inet_ntoa(peer[0:4]),
                        struct.unpack('!H', peer[4:6])[0]) for peer in peers]

        return hosts_ports

    def _build_url(self, torrent, etype):
        """Create the url that is sent to the tracker. The etype that is
        specified must be one of started, stopped or finished."""

        announce_query = {
            'info_hash': torrent.info_hash,
            'peer_id': self.factory.client.client_id,
            'port': torrent.port,
            'uploaded': torrent.uploaded,
            'downloaded': torrent.downloaded,
            'left': torrent.left,
            'event': etype }

        url = torrent.tracker_url + '?' + urllib.urlencode(announce_query)

        return url

class TrackerClient(object):

    trackers = {'http': HTTPTracker, 'https': HTTPTracker, 'udp': UDPTracker}

    def __init__(self, client):
        self.client = client

    @defer.inlineCallbacks
    def get_peers(self, torrent):
        for url in chain.from_iterable(torrent.announce_list):
            try:
                torrent.tracker_url = url
                protocol, host, port = self._parse(url)
                self.tracker = self.trackers[protocol](self, host, port)
                peers = yield self.tracker.announce(torrent)
                defer.returnValue(peers)
            except Exception as e:
                print e
                pass
        else:
            print 'Unable to connect to a tracker for %s' % torrent.filename
            self.client.delete_torrent(torrent)

    @staticmethod
    def _parse(url):
        pieces = url.split(':')
        if len(pieces) == 3:
            protocol, host, port = pieces
            port = int(port.split('/')[0])
        elif len(pieces) == 2:
            protocol, host = pieces
            port = None
        host = host.strip('/')

        return protocol, host, port

class AnnounceError(Exception):
    pass
