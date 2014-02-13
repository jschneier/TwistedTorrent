import unittest
from twistedtorrent.utils import parse_url, decode_hosts_ports

class TestUtils(unittest.TestCase):

    def test_parse_url(self):
        url_results = [('http://www.google.com:80', ('http', 'www.google.com', 80)),
                       ('http://www.google.com', ('http', 'www.google.com', None))]
        for url, results in url_results:
            self.assertEqual(parse_url(url), results)

    def test_decode_hosts_ports_bad_size_raises(self):
        self.assertRaises(ValueError, decode_hosts_ports, '12345678910')

    def test_decode_hosts_port(self):
        compact = '\x7f\x00\x00\x01\x1f\x90'
        decoded = decode_hosts_ports(compact)
        self.assertEqual(decoded, [('127.0.0.1', 8080)])

if __name__ == '__main__':
    unittest.main()
