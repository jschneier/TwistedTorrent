import time
import copy
import logging
from twisted.internet import defer

from .exceptions import NoValidTorrent
from .torrent import ActiveTorrent
from .tracker import TrackerClient
from .constants import CLIENT_ID_VER
from .btencode import BTEncodeError, BTDecodeError

logging.basicConfig(level=logging.DEBUG)

class TorrentClient(object):
    """A torrent client object. Provides the highest level of abstraction."""

    def __init__(self, torrents, port=6881):
        self.client_id = (CLIENT_ID_VER + str(time.time()))[:20]
        self.port = port
        self.torrents = set()
        if isinstance(torrents, basestring):
            torrents = [torrents]
        for torrent in torrents:
            try:
                self.torrents.add(ActiveTorrent(self, torrent))
            except (BTEncodeError, BTDecodeError):
                logging.exception('Invalid torrent btencoded file: %s', torrent)
            except IOError:
                logging.exception('Issue opening torrent file: %s', torrent)
        if not self.torrents:
            raise NoValidTorrent()
        self.tracker = TrackerClient(self)

        from twisted.internet import reactor
        reactor.callWhenRunning(self.start)
        reactor.run()

    def start(self):
        torrents = copy.copy(self.torrents)
        for torrent in torrents:
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
