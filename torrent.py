import sys
import tempfile
import btencode
from hashlib import sha1
from constants import BSIZE
from piece import Piece, FinalPiece
from protocol import PeerProtocolFactory

DEBUG = False

class Torrent(object):
    """Container for parsed metadata from a .torrent file."""

    def __init__(self, filename):
        self.filename = filename
        self.parse_metainfo()

    def parse_metainfo(self):
        try:
            with open(self.filename) as tor:
                torrent_dict = btencode.btdecode(tor.read())
        except btencode.BTDecodeError:
            print 'BTDecodeError handling %s' % self.filename
            sys.exit(1)
        except IOError:
            print 'IOError handling %s' % self.filename
            sys.exit(1)

        self.announce_url = torrent_dict['announce']
        info = torrent_dict['info']
        self.info_hash = sha1(btencode.btencode(info)).digest()
        self.piece_length = info['piece length']

        if not 'files' in info:
            self.length = info['length']
            self.names_length = [[info['name'], self.length]]
        else:
            self.length = sum(f['length'] for f in info['files'])
            self.names_length = [(f['path'][0], f['length'])
                                    for f in info['files']]

        # break string pieces up into a list of those pieces
        pieces_string = info['pieces']
        hashes = [pieces_string[i: i+20] for i in xrange(0, len(pieces_string), 20)]
        num_pieces = len(hashes)
        blocks = self.piece_length / BSIZE

        # calculate size of last piece
        leftover = self.length - ((num_pieces - 1) * self.piece_length)
        final_blocks = int(round(float(leftover) / BSIZE))
        final_size = leftover % BSIZE

        self.pieces = [Piece(hashes[i], blocks) for i in xrange(num_pieces-1)]
        self.pieces.append(FinalPiece(hashes[-1], final_blocks, final_size))

class ActiveTorrent(Torrent):
    """Represents a torrent that is in the process of being downloaded.
    Responsible for figuring out which strategies the factory should be passing
    down to the protocols and for handling all writing of file data."""

    def __init__(self, client, filename):
        super(ActiveTorrent, self).__init__(filename)
        self.client = client
        self.uploaded = 0
        self.downloaded = 0
        self.factory = PeerProtocolFactory(client, self)
        self.outfile = tempfile.TemporaryFile()
        self.to_dl = set(range(len(self.pieces)))

    def add_block(self, index, offset, block):
        piece = self.pieces[index]
        if piece.has_block(offset): return  # same block coming in again

        piece.add(offset, block)
        if piece.is_full():
            if piece.check_hash():
                self.write_piece(index)
                self.factory.update_successful_piece(index)
                if not self.left:
                    self.factory.strategy = self.factory.stop
                    self.finish()
            else:
                # hash didn't match, reset the piece
                piece.clear()

    def write_piece(self, index):
        data = self.pieces[index].full_data
        self.outfile.seek(self.piece_length * index)
        self.outfile.write(data)
        self.downloaded += len(data)
        self.to_dl.remove(index)

    def get_block(self):
        if not self.to_dl: return
        index = min(self.to_dl)
        offset_index = self.pieces[index].next_piece
        return index, offset_index

    def finish(self):
        self.write_files()
        self.client.delete_torrent(self)

    def connect_to_peer(self, (host, port)):
        from twisted.internet import reactor
        reactor.connectTCP(host, port, self.factory)

    def write_files(self):
        self.outfile.seek(0)
        for fname, size in self.names_length:
            with open(fname, 'w') as cur:
                cur.write(self.outfile.read(size))
        self.outfile.close()  # closing temp file deletes it

    @property
    def left(self):
        return self.length - self.downloaded

if __name__ == '__main__':
    from client import TorrentClient
    TorrentClient(sys.argv[1]).start()
