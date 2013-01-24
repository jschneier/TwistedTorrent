import time
import copy
from twisted.internet import defer

from torrent import ActiveTorrent
from tracker import TrackerClient
from constants import CLIENT_ID_VER

class TorrentClient(object):
    """A torrent client object. Provides the highest level of abstraction."""

    def __init__(self, torrents):
        self.client_id = (CLIENT_ID_VER + str(time.time()))[:20]
        self.port = 6881
        if not torrents:
            raise ValueError('Must supply at least 1 torrent file')
        self.torrents = {ActiveTorrent(self, torrent) for torrent in torrents}
        self.tracker = TrackerClient(self)

        from twisted.internet import reactor
        reactor.callWhenRunning(self.start)
        reactor.run()

    def start(self):
        tors = copy.copy(self.torrents)
        for torrent in tors:
            self._download(torrent)

    @defer.inlineCallbacks
    def _download(self, torrent):
        hosts_ports = yield self.tracker.get_peers(torrent)
        if hosts_ports is not None:
            for host_port in hosts_ports:
                torrent.connect_to_peer(host_port)

    def delete_torrent(self, torrent):
        '''Remove a torrent that has finished downloading or was unable to
        connect to any trackers.'''

        self.torrents.remove(torrent)
        if not self.torrents:
            self.stop()

    def stop(self):
        from twisted.internet import reactor
        reactor.stop()
