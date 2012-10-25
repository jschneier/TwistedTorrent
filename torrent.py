import sys
import math
import bencode
from hashlib import sha1
from collections import defaultdict
from protocol import PeerProtocolFactory

range = xrange

class Torrent(object):
    """Container for parsed metadata from a .torrent file."""
 
    def __init__(self, filename):
        self.filename = filename
        self.parse_metainfo()

    def parse_metainfo(self):
        torrent_dict = bencode.bdecode(open(self.filename).read())

        self.announce_url = torrent_dict['announce']
        self.info = torrent_dict['info']
        self.info_hash = sha1(bencode.bencode(self.info)).digest()
        self.p_length = self.info['piece length']

        #break string pieces up into a list of those pieces
        pieces_string = self.info['pieces']
        self.pieces = [pieces_string[i: i+20]
                        for i in range(0, len(pieces_string), 20)]

        self.n_pieces = len(self.pieces)
        self.num_files = len(self.info['files']) if 'files' in self.info else 1
        if self.num_files == 1:
            self.length = self.info['length']
            self.names = [self.info['name']] #make it a list so we can iterate
        else:
            self.length = sum(f['length'] for f in self.info['files'])
            self.names_length = [(f['path'][0], f['length'])
                                    for f in self.info['files']]

        #making assumption about even division
        self.blocks_pp = self.length / self.p_length

        #bytes leftover for the last block
        leftover = self.length - ((self.n_pieces - 1) * self.p_length)
        self.blocks_fp = int(math.ceil(float(leftover) / self.p_length))

class ActiveTorrent(Torrent):
    """Represents a torrent that is in the process of being downloaded."""

    def __init__(self, client, filename):
        super(ActiveTorrent, self).__init__(filename)
        self.client = client
        self.uploaded = 0
        self.downloaded = 0
        self.index_piece = {i: piece for i, piece in enumerate(self.pieces)}

        #-1 because we need to set the number of blocks for the final piece
        self.piece_block_flags = [[0 for _ in range(self.blocks_pp)]
                                        for _ in range(self.n_pieces-1)]
        self.piece_block_flags.append([0 for _ in range(self.block_fp)])

        self.piece_block = defaultdict(lambda: defaultdict(str))

        self.factory = PeerProtocolFactory(client, self)
        self.outfile = 'temp_' + self.info_hash

    def add_block(self, index, offset, block):
        b_index = self.blocks_pp * offset / self.p_length
        self.piece_block[index][b_index] = block
        self.piece_block_flags[index][b_index] = 1

        if all(self.piece_block_flags[index]):
            if self.check_hash(index):
                self.write_piece(index)
            else:
                raise ValueError('Incorrent hash obtained')

    def check_hash(self, index):
        return self.index_piece[index] == sha1(self._assemble_block(index)).digest()

    def write_piece(self, index):
        with open(self.outfile, 'ab') as out:
            out.seek(self.p_length * index)
            out.write(self._assemble_block(index))
            self.clean_up(index)

    def clean_up(self, index):
        del self.index_piece[index]
        del self.piece_block[index]
        if not self.left: #torrent is finished downloading
            self.finish()

    def finish(self):
        del self.factory
        self.client.delete_torrent(self)

    def connect_to_peer(self, (host, port)):
        from twisted.internet import reactor
        reactor.connectTCP(host, port, self.factory)

    def _assemble_block(self, index):
        return ''.join(self.piece_block[index][i] for i in
                        range(len(self.piece_block[index])))

    @property
    def left(self):
        return self.length - self.downloaded

if __name__ == '__main__':
    from client import TorrentClient
    client = TorrentClient(ActiveTorrent(sys.argv[1]))
