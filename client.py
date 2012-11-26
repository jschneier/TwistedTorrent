import time
import urllib
import struct
import socket
import btencode
from torrent import ActiveTorrent
from constants import CLIENT_ID_VER
from twisted.web.client import getPage

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

    def _download(self, torrent):
        d = self.announce(torrent, 'started')
        def dl(host_ports):
            for host_port in host_ports:
                torrent.connect_to_peer(host_port)
        d.addCallback(dl)

    def announce(self, torrent, etype):
        """Encode and send the request to the tracker and then parse the
        response to get the host and ports of the specified peers."""

        url = self._build_url(torrent, etype)
        d = getPage(url, timeout=5)

        def parse_response(response):
            if not response:
                raise AnnounceError('No response from tracker for url %s' % url)

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

        d.addCallback(parse_response)
        return d

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

        base = torrent.announce_url
        url = base + '?' + urllib.urlencode(announce_query)

        return url

    def delete_torrent(self, torrent):
        '''Remove a torrent that has finished downloading.'''

        self.torrents.remove(torrent)
        if not self.torrents:
            self.stop()

    def stop(self):
        from twisted.internet import reactor
        reactor.stop()

class AnnounceError(Exception):
    pass
