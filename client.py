import os
import urllib
import bencode
from torrent import ActiveTorrent

class TorrentClient(object):
    """A torrent client object, makes the request to the tracker as specified 
    and then connects to each peer as necessary."""

    def __init__(self, *torrents):
        self.client_id = (str(os.getpid()) + '901asdf0293fasljz23raasd')[:20]
        self.port = 6881
        if not torrents:
            raise ValueError('Must supply at least 1 torrent file')
        self.torrents = [ActiveTorrent(self, torrent) for torrent in torrents]

    def start(self):
        for torrent in self.torrents:
            self._download(torrent)
        from twisted.internet import reactor
        reactor.run()

    def _download(self, torrent):
        host_ports = self.announce(torrent, type='started')
        for host_port in host_ports:
            torrent.connect_to_peer(host_port)

    def announce(self, torrent, type=None):
        """Encode and send the request to the tracker and then parse the
        response to get the host and ports of the specified peers."""

        url = self._build_url(torrent, type)

        response = urllib.urlopen(url).read()
        if not response:
            raise AnnounceError('No response from tracker for url %s' % url)

        tracker_dict = bencode.bdecode(response)

        if 'failure reason' in tracker_dict:
            raise AnnounceError('''failure reason key in tracker response\
                                    %s:''' % tracker_dict['failure reason'])

        peers_raw = tracker_dict['peers']
        if isinstance(peers_raw, dict):
            raise AnnounceError('peers as dictionary model not implemented')

        peers_bytes = (peers_raw[i:i+6] for i in range(0, len(peers_raw), 6))
        peers = (map(ord, peer) for peer in peers_bytes)
        host_ports = [('.'.join(map(str, peer[0:4])), 256 * peer[4] + peer[5]) for peer in peers]

        return host_ports

    def _build_url(self, torrent, type):
        """Create the url that is sent to the tracker. The type that is
        specified must be one of started, stopped or finished."""

        if type is None:
            raise AnnounceError('Must specify type of request, eg. started')

        announce_query = {
            'info_hash': torrent.info_hash,
            'peer_id': self.client_id,
            'port': self.port,
            'uploaded': torrent.uploaded,
            'downloaded': torrent.downloaded,
            'left': torrent.left,
            'event': type
        }

        base = torrent.announce_url
        url = base + '?' + urllib.urlencode(announce_query)

        return url

    def delete_torrent(self, torrent):
        '''Remove a torrent that has finished downloading.'''

        torrent_id = id(torrent)
        for index, torrent in enumerate(self.torrents):
            if id(torrent) == torrent_id:
                deletion_index = index
                break
        else:
            raise Exception('No torrents in the list with same id')

        del self.torrents[deletion_index]

class AnnounceError(Exception):
    pass
