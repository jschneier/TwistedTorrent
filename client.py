import time
import urllib
import struct
import socket
import btencode
import itertools
from torrent import ActiveTorrent
from constants import CLIENT_ID_VER
from twisted.web.client import getPage
from twisted.internet import defer

class TorrentClient(object):
    """A torrent client object, makes the request to the tracker as specified
    and then connects to each peer as necessary."""

    def __init__(self, *torrents):
        self.client_id = (CLIENT_ID_VER + str(time.time()))[:20]
        self.port = 6881
        if not torrents:
            raise ValueError('Must supply at least 1 torrent file')
        self.torrents = {ActiveTorrent(self, torrent) for torrent in torrents}

        from twisted.internet import reactor
        reactor.callWhenRunning(self.start)
        reactor.run()

    def start(self):
        for torrent in self.torrents:
            self._download(torrent)

    @defer.inlineCallbacks
    def _download(self, torrent):
        hosts_ports = yield self.get_peers(torrent)
        if hosts_ports is not None:
            for host_port in hosts_ports:
                torrent.connect_to_peer(host_port)

    @defer.inlineCallbacks
    def get_peers(self, torrent):
        for url in itertools.chain.from_iterable(torrent.announce_list):
            try:
                torrent.tracker_url = url
                peers = yield self.http_announce(torrent)
                defer.returnValue(peers)
            except Exception:
                pass
        else:
            print 'Unable to connect to a tracker for %s' % torrent.filename
            self.delete_torrent(torrent)

    @defer.inlineCallbacks
    def http_announce(self, torrent):
        """Encode and send the request to the tracker and then parse the
        response to get the host and ports of the specified peers."""

        url = self._build_url(torrent, 'started')
        response = yield getPage(url, timeout=5)

        defer.returnValue(self.parse_response(response))

    def parse_response(self, response):

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
            'peer_id': self.client_id,
            'port': self.port,
            'uploaded': torrent.uploaded,
            'downloaded': torrent.downloaded,
            'left': torrent.left,
            'event': etype }

        url = torrent.tracker_url + '?' + urllib.urlencode(announce_query)

        return url

    def delete_torrent(self, torrent):
        '''Remove a torrent that has finished downloading or was unable to
        connect to any trackers.'''

        self.torrents.remove(torrent)
        if not self.torrents:
            self.stop()

    def stop(self):
        from twisted.internet import reactor
        reactor.stop()

class AnnounceError(Exception):
    pass
