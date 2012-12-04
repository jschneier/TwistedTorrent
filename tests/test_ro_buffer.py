import unittest
from twistedbits.read_once_buffer import ReadOnceBuffer

class ReadOnceBufferTest(unittest.TestCase):
    
    def setUp(self):
        self.buf = ReadOnceBuffer('spameggs')

    def test_identity(self):
        self.assertEquals(self.buf, ReadOnceBuffer('spameggs'))

    def test_addition(self):
        self.assertEquals(self.buf + 'foo', ReadOnceBuffer('spameggsfoo'))

        #addition returns a new object
        self.assertIsNot(self.buf + 'foo', self.buf)

    def test_inplace_addition(self):
        self.buf += 'bar'
        self.assertEquals(self.buf, ReadOnceBuffer('spameggsbar'))

        #inplace addition returns the same object
        self._buf = self.buf
        self.buf += 'foo'
        self.assertIs(self.buf, self._buf)

    def test_raise_out_of_bounds(self):
        self.assertRaises(IndexError, lambda: self.buf[200])

    def test_indexing_deletes(self):
        self.assertEquals(ord('p'), self.buf[1])
        self.assertEquals(ReadOnceBuffer('sameggs'), self.buf)

    def test_slicing_deletes(self):
        self.assertEquals(ReadOnceBuffer('ame'), self.buf[2:5])
        self.assertEquals(ReadOnceBuffer('spggs'), self.buf)

    def test_full_deletion(self):
        self.assertEquals(ReadOnceBuffer('spameggs'), self.buf[:])
        self.assertEquals(ReadOnceBuffer(), self.buf)

    def test_peek_index_doesnt_delete(self):
        self.assertEquals(self.buf.peek(2), ord('a'))
        self.assertEquals(self.buf, ReadOnceBuffer('spameggs'))

    def test_peek_slice_doesnt_delete(self):
        self.assertEquals(self.buf.peek(2, 5), ReadOnceBuffer('ame'))
        self.assertEquals(self.buf, ReadOnceBuffer('spameggs'))

if __name__ == '__main__':
    unittest.main()
