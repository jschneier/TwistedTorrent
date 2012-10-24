import sys
import math
import hashlib
import bencode
from protocol import PeerProtocolFactory

class Torrent(object):
    """Container for parsed metadata from a .torrent file."""
 
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
        self.pieces = [pieces_string[i: i+20]
                        for i in xrange(0, len(pieces_string), 20)]

        self.num_files = len(self.info['files']) if 'files' in self.info else 1
        if self.num_files == 1:
            self.length = self.info['length']
            self.names = [self.info['name']] #make it a list so we can iterate
        else:
            self.length = sum(f['length'] for f in self.info['files'])
            self.names_length = [(f['path'][0], f['length'])
                                    for f in self.info['files']]

        #making assumption about even division
        self.blocks_pp = self.length / self.piece_length

        #bytes leftover for the last block
        leftover = self.length - ((len(self.pieces) - 1) * self.piece_length)
        self.blocks_fp = int(math.ceil(float(leftover) / self.piece_length))

class ActiveTorrent(Torrent):
    """Represents a torrent that is in the process of being downloaded."""

    def __init__(self, client, filename):
        super(ActiveTorrent, self).__init__(filename)
        self.client = client
        self.uploaded = 0
        self.downloaded = 0
        self.index_piece = {i: piece for i, piece in enumerate(self.pieces)}
        self.index_flags = [0 for _ in xrange(len(self.pieces))]

        #-1 because we need to set the number of blocks for final pieces
        self.piece_block_index = {piece: {i: ''} for piece in self.pieces for i
                                        in xrange(self.blocks_pp-1)}
        self.piece_block_index[self.pieces[-1]] = {i: '' for i in
                                            xrange(self.blocks_fp)}
        self.factory = PeerProtocolFactory(client, self)
        self.peers = set()
        self.outfile = 'temp_' + self.info_hash

    @property
    def left(self):
        return self.length - self.downloaded

    @property
    def connections(self):
        return len(self.peers)

    def write_piece(self, index, data):
        #TODO make sure this works for the last piece
        with open(self.outfile, 'ab') as out:
            out.seek(self.piece_length * index)
            out.write(data)
        #TODO set things to one and clear out the buffer
        self.downloaded += len(data)

    def connect_to_peer(self, (host, port)):
        from twisted.internet import reactor
        reactor.connectTCP(host, port, self.factory)
        self.peers.add((host, port))

if __name__ == '__main__':
    from client import TorrentClient
    client = TorrentClient(ActiveTorrent(sys.argv[1]))
