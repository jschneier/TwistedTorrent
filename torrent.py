import os
import sys
import math
import bencode
from hashlib import sha1
from random import sample, randint
from constants import bsize
from piece import Piece, FinalPiece
from protocol import PeerProtocolFactory

DEBUG = True

class Torrent(object):
    """Container for parsed metadata from a .torrent file."""
 
    def __init__(self, filename):
        self.filename = filename
        self.parse_metainfo()

    def parse_metainfo(self):
        torrent_dict = bencode.bdecode(open(self.filename).read())

        self.announce_url = torrent_dict['announce']
        info = torrent_dict['info']
        self.info_hash = sha1(bencode.bencode(info)).digest()
        self.piece_length = info['piece length']

        if not 'files' in info:
            self.length = info['length']
            self.names_length = [[info['name'], self.length]]
        else:
            self.length = sum(f['length'] for f in info['files'])
            self.names_length = [(f['path'][0], f['length'])
                                    for f in info['files']]

        #break string pieces up into a list of those pieces
        pieces_string = info['pieces']
        hashes = [pieces_string[i: i+20] for i in xrange(0, len(pieces_string), 20)]
        num_pieces = len(hashes)
        blocks = self.piece_length / bsize

        #calculate size of last piece
        leftover = self.length - ((num_pieces - 1) * self.piece_length)
        final_blocks = int(math.ceil(float(leftover) / self.piece_length))

        self.pieces = [Piece(hashes[i], blocks) for i in xrange(num_pieces-1)]
        self.pieces.append(FinalPiece(hashes[-1], final_blocks, leftover))

class ActiveTorrent(Torrent):
    """Represents a torrent that is in the process of being downloaded."""

    def __init__(self, client, filename):
        super(ActiveTorrent, self).__init__(filename)
        self.client = client
        self.uploaded = 0
        self.downloaded = 0
        self.factory = PeerProtocolFactory(client, self)
        self.out_name = 'temp_ ' + str(randint(0, 100000))
        self.outfile = open(self.out_name, 'w')
        self.to_dl = set(range(len(self.pieces)))

    def add_block(self, index, offset, block):
        if index not in self.to_dl: return #multiple requests for same piece

        piece = self.pieces[index]
        piece.add(offset, block)
        if piece.is_full:
            if piece.check_hash():
                self.write_piece(index)
            else:
                raise ValueError('Shit, hash didn\'t match')

    def write_piece(self, index):
        data = self.pieces[index].full_data
        self.outfile.seek(self.piece_length * index)
        self.outfile.write(data)
        self.downloaded += len(data)
        self.clean_up(index)

    def clean_up(self, index):
        self.to_dl.remove(index)
        if not self.left: #torrent is finished downloading
            self.finish()

    def get_block(self):
        if not self.to_dl: return
        index, = sample(self.to_dl, 1)
        offset_index = self.pieces[index].first_nothave()
        return index, offset_index

    def finish(self):
        self.outfile.close()
        self.write_files()
        del self.factory
        self.client.delete_torrent(self)

    def connect_to_peer(self, (host, port)):
        from twisted.internet import reactor
        reactor.connectTCP(host, port, self.factory)

    def write_files(self):
        with open(self.out_name) as out:
            for fname, size in self.names_length:
                with open(fname, 'w') as cur:
                    cur.write(out.read(size))
        os.remove(self.out_name)

    @property
    def left(self):
        return self.length - self.downloaded

if __name__ == '__main__':
    from client import TorrentClient
    client = TorrentClient(ActiveTorrent(sys.argv[1]))
