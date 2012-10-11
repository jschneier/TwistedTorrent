import sys
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
        self.num_files = len(self.info['files']) if 'files' in self.info else 1

        if self.num_files == 1:
            self.length = self.info['length']
        else:
            self.length = sum(int(f['length']) for f in self.info['files'])

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
        tracker_url = self.torrent.announce_url + '?' + urllib.urlencode(announce_query)
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

if __name__ == '__main__':
    torrent = Torrent(sys.argv[1])
    track = Tracker(torrent=torrent)
