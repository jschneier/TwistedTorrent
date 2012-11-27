import struct
import socket
import urllib
import btencode
from itertools import chain
from twisted.internet import defer
from twisted.web.client import getPage

class TrackerClient(object):

    def __init__(self, client):
        self.client = client

    @defer.inlineCallbacks
    def get_peers(self, torrent):
        for url in chain.from_iterable(torrent.announce_list):
            try:
                torrent.tracker_url = url
                peers = yield self.http_announce(torrent)
                defer.returnValue(peers)
            except Exception:
                pass
        else:
            print 'Unable to connect to a tracker for %s' % torrent.filename
            self.client.delete_torrent(torrent)

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
            'peer_id': self.client.client_id,
            'port': self.client.port,
            'uploaded': torrent.uploaded,
            'downloaded': torrent.downloaded,
            'left': torrent.left,
            'event': etype }

        url = torrent.tracker_url + '?' + urllib.urlencode(announce_query)

        return url

class AnnounceError(Exception):
    pass
