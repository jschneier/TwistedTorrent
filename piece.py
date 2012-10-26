import re
import hashlib
from constants import bsize

class Piece(object):

    check = re.compile(r'0')
    
    def __init__(self, hash, blocks):
        self.hash = hash
        self.blocks = '0' * blocks
        self.block_data = {}

    @property
    def is_full(self):
        return bool(Piece.check.search(self.blocks))

    def first_nothave(self):
        return Piece.check.search(self.blocks).start()

    def add(self, offset, data):
        #offset is in bytes, need to get to index
        index = offset / bsize
        self.block_data[index] = data
        self.blocks = self.blocks[:index] + '1' + self.blocks[index+1:]

    @property
    def full_data(self):
        return ''.join(self.block_data[i] for i in xrange(len(self.blocks)))

    def check_hash(self):
        return self.hash == hashlib.sha1(self.full_data).digest()

class FinalPiece(Piece):
    pass
