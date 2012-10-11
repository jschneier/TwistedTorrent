import sys
import time
import urllib
import bencode

class TrackerTalkError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return self.error

class Tracker(object):
    '''
    A torrent tracker object, connects over HTTP[s], responsible for routing
    requests. 1 to 1 relationship between torrent and tracker.

    Requires an instance of the Torrent class object to be passed to it.
    '''

    def __init__(self, torrent, **kwargs):
        self.client_id = str(time.time()) + '901asdf0293fasljz23raasd'
        if len(self.client_id) > 20:
            self.client_id = self.client_id[0:20]
        self.port = 6881
        self.torrent = torrent
        self.decode_and_parse()

    def _build_url(self, completed=False):
        event = 'completed' if completed else 'started'

        announce_query = {
            'info_hash': self.torrent.info_hash,
            'peer_id': self.client_id,
            'port': self.port,
            'uploaded': 0,
            'downloaded': 0,
            'left': self.torrent.length,
            'event': event,
        }
        base = self.torrent.announce_url
        tracker_url = base + '?' + urllib.urlencode(announce_query)
        return tracker_url

    def request(self, **kwargs):
        url = self._build_url(**kwargs)
        response = urllib.urlopen(url).read()
        if not response:
            raise TrackerTalkError('No response from tracker for url %s' % url)
        return response

    def decode_and_parse(self):
        response = self.request()
        tracker_dict = bencode.bdecode(response)

        if 'failure reason' in tracker_dict:
            raise TrackerTalkError('''failure reason key in tracker response\
                                    %s:''' % tracker_dict['failure reason'])

        peers_raw = tracker_dict['peers']
        if isinstance(peers_raw, dict):
            raise TrackerTalkError('peers as dictionary model not implemented')

        temp = (peers_raw[i:i+6] for i in range(0, len(peers_raw), 6))
        peers = (map(ord, peer) for peer in temp)
        ip_ports = [('.'.join(map(str, peer[0:4])), 256 * peer[4] + peer[5]) for peer in peers]
        return ip_ports

if __name__ == '__main__':
    from torrent import Torrent
    torrent = Torrent(sys.argv[1])
    track = Tracker(torrent=torrent)
