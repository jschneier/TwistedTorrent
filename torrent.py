import time
import urllib
import hashlib
import bencode

class TrackerTalkError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return self.error

class Torrent(object):
    '''
    Accepts a single .torrent file and parses it for metadata
    '''
 
    def __init__(self, filename):
        self.filename = filename
        self.parse_metainfo()

    def parse_metainfo(self):
        torrent_dict = bencode.bdecode(open(self.filename).read())

        self.announce_url = torrent_dict['announce']
        self.info = torrent_dict['info']
        self.info_hash = hashlib.sha1(bencode.bencode(self.info)).digest()
        self.piece_length = self.info['piece length']
        self.num_files = 1 if 'file' in self.info else len(self.info['files'])
        ###actually do
        self.length = 26356589

class Tracker(object):
    '''
    A torrent tracker object, connects over HTTP[s], responsible for routing
    requests
    '''

    def __init__(self, **kwargs):
        self.client_id = str(time.time()) + '901asdf0293fasljz23raasd'
        if len(self.client_id) > 20:
            self.client_id = self.client_id[0:20]
        self.port = 6881

    def _build_url(self, torrent, completed=False):
        event = 'completed' if completed else 'started'

        announce_query = {
            'info_hash': torrent.info_hash,
            'peer_id': self.client_id,
            'port': self.port,
            'uploaded': 0,
            'downloaded': 0,
            'left': torrent.length, #remove
            'event': event,
        }
        tracker_url = torrent.announce_url + '?' + urllib.urlencode(announce_query)
        return tracker_url

    def request(self, torrent):
        url =  self._build_url(torrent)
        response = urllib.urlopen(url).read()
        if not response:
            raise TrackerTalkError('No response from tracker for url %s' % url)
        return response

if __name__ == '__main__':
    track = Tracker()
    torrent = Torrent('bar.torrent')
    track.request(torrent)
