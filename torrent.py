import sys
import hashlib
import bencode
from protocol import PeerProtocolFactory

class Torrent(object):
    '''
    Container for parsed metadata from a .torrent file.
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

        #break string pieces up into a list of those pieces
        pieces_string = self.info['pieces']
        self.pieces = [pieces_string[i:i+20]
                        for i in xrange(0, len(pieces_string), 20)]

        self.num_files = len(self.info['files']) if 'files' in self.info else 1
        if self.num_files == 1:
            self.length = self.info['length']
            self.names = [self.info['name']] #make it a list so we can iterate
        else:
            self.length = sum(f['length'] for f in self.info['files'])
            self.names_length = [(f['path'][0], f['length'])
                                    for f in self.info['files']]

class ActiveTorrent(Torrent):
    '''
    Represents a torrent that is in the process of being downloaded.
    '''

    def __init__(self, filename):
        super(ActiveTorrent, self).__init__(filename)
        self.uploaded = 0
        self.downloaded = 0
        self.factory = PeerProtocolFactory(self)

    @property
    def left(self):
        return self.length - self.downloaded

    @property
    def connections(self):
        return len(self.peers)

    def connect_to_peer(self, (host, port)):
        from twisted.internet import reactor
        reactor.connectTCP(host, port, self.factory)

if __name__ == '__main__':
    from client import TorrentClient
    client = TorrentClient()
    torrent = ActiveTorrent(sys.argv[1])
    client.announce(torrent)
