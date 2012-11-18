import unittest
from btencode import decode_string, decode_int, decode_list

class TestDecodeString(unittest.TestCase):

    def test_single_number(self):
        self.assertEquals(('trac', 6), decode_string('4:trac', 0))
class TestDecodeInt(unittest.TestCase):

    def test_single_number(self):
        self.assertEquals((3, 2), decode_int('i3e', 0))

    def test_octal_encoding_raises(self):
        self.assertRaises(ValueError, decode_int, 'i00e', 0)

class TestDeocdeList(unittest.TestCase):
    
    def test_single_string_list(self):
        self.assertEquals(['spam'], decode_list('l4:spame', 0))

    def test_multi_string_list(self):
        self.assertEquals(['spam', 'spam'], decode_list('l4:spamel4:spame', 0))

if __name__ == '__main__':
    unittest.main()
