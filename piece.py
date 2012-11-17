import hashlib
import bitarray
from constants import BSIZE

class Piece(object):

    def __init__(self, hash, blocks):
        self.hash = hash
        self.blocks = bitarray.bitarray(blocks)
        self.block_data = {}
        self.next_piece = 0

    @property
    def is_full(self):
        return self.next_piece == len(self.blocks)

    def add(self, offset, data):
        #offset is in bytes, need to get to index
        index = offset / BSIZE
        self.block_data[index] = data
        self.blocks[index] = True
        self.next_piece += 1

    def has_block(self, offset):
        #offset is in bytes, need to get to index
        index = offset / BSIZE
        return self.blocks[index] == True

    @property
    def full_data(self):
        return ''.join(str(self.block_data[i]) for i in xrange(len(self.blocks)))

    def check_hash(self):
        return self.hash == hashlib.sha1(self.full_data).digest()

    def get_size(self, offset_index):
        return BSIZE

class FinalPiece(Piece):

    def __init__(self, hash, blocks, fsize):
        super(FinalPiece, self).__init__(hash, blocks)
        self.fsize = fsize

    def is_last_block(self, offset_index):
        return offset_index == len(self.blocks) - 1

    def get_size(self, offset_index):
        return self.fsize if self.is_last_block(offset_index) else BSIZE
