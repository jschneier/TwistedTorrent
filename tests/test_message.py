import unittest
from message import Message
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

if __name__ == '__main__':
    unittest.main()
