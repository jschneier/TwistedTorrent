import unittest
from btencode import btdecode, btencode, BTDecodeError, BTEncodeError

class TestBTDecode(unittest.TestCase):

    def test_string(self):
        self.assertEquals('trac', btdecode('4:trac'))

    def test_int(self):
        self.assertEquals(3, btdecode('i3e'))

    def test_list(self):
        self.assertEquals(['spam', 3, 'eggs'], btdecode('l4:spami3e4:eggse'))

    def test_dict(self):
        self.assertEquals({'cow': 'moo', 'spam': 'eggs'}, btdecode('d3:cow3:moo4:spam4:eggse'))

    def test_octal_encode_raises_btdecode_error(self):
        self.assertRaises(BTDecodeError, btdecode, 'i00e')

    def test_extra_raises_btdecode_error(self):
        self.assertRaises(BTDecodeError, btdecode, 'l4spamel')

class TestBTEncode(unittest.TestCase):

    def test_string(self):
        self.assertEquals('4:trac', btencode('trac'))

class TestEncodeString(unittest.TestCase):

    def test_string(self):
        self.assertEquals('4:trac', btencode('trac'))

class TestEncodeInt(unittest.TestCase):

    def test_int(self):
        self.assertEquals('i3e', btencode(3))

class TestEncodeList(unittest.TestCase):

    def test_list(self):
        self.assertEquals('l4:spami3ei4e4:spame', btencode(['spam', 3, 4, 'spam']))

class TestEncodeDict(unittest.TestCase):

    def test_dict(self):
        self.assertEquals('d3:cow3:moo4:spam4:eggse', btencode({'cow': 'moo', 'spam': 'eggs'}))

if __name__ == '__main__':
    unittest.main()
