import unittest
from message import Message
from constants import BSIZE
from bitarray import bitarray

class MessageTest(unittest.TestCase):

    def test_keep_alive(self):
        self.assertEquals(Message('keep_alive'), '\x00\x00\x00\x00')

    def test_choke(self):
        self.assertEquals(Message('choke'), '\x00\x00\x00\x01\x00')

    def test_unchoke(self):
        self.assertEquals(Message('unchoke'), '\x00\x00\x00\x01\x01')

    def test_interested(self):
        self.assertEquals(Message('interested'), '\x00\x00\x00\x01\x02')

    def test_not_interested(self):
        self.assertEquals(Message('not_interested'), '\x00\x00\x00\x01\x03')

    def test_have(self):
        self.assertEquals(Message('have', piece_index=19),
                                    '\x00\x00\x00\x05\x04\x00\x00\x00\x13')

    def test_bitfield(self):
        bit = bitarray('01011000')
        self.assertEquals(Message('bitfield', bitfield=bit),
                                    '\x00\x00\x00\x02\x05\x58')

    def test_request(self):
        self.assertEquals(Message('request', index=4,
                                    offset=2 * BSIZE, length=BSIZE),
                                    '\x00\x00\x00\x0d\x06\x00\x00\x00\x04\x00\x00\x80\x00\x00\x00\x40\x00')

    def test_piece(self):
        self.assertEquals(Message('piece', index=4,
                                    offset=2 * BSIZE, block=bitarray('00000001')),
                                   '\x00\x00\x00\x0a\x07\x00\x00\x00\x04\x00\x00\x80\x00\x01')

    def test_cancel(self):
        self.assertEquals(Message('cancel', index=4,
                                    offset=2 * BSIZE, length=BSIZE),
                                    '\x00\x00\x00\x0d\x08\x00\x00\x00\x04\x00\x00\x80\x00\x00\x00\x40\x00')
    def test_port(self):
        self.assertEquals(Message('port', listen_port=8000),
                                    '\x00\x00\x00\x03\x09\x1f\x40')

if __name__ == '__main__':
    unittest.main()
