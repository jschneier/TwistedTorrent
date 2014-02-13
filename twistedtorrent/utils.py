import random
import string
import struct
import socket
import urlparse

def parse_url(url):
    parsed = urlparse.urlparse(url)
    return parsed.scheme, parsed.hostname, parsed.port

def nrandom(n, chars=string.printable):
    """Return a random byte string of length n."""
    return ''.join([random.choice(chars) for _ in xrange(n)])

def decode_hosts_ports(peers_raw):
    """Decode a compact byte string of hosts and ports into a list of tuples.
    Peers_raw's length must be a multiple of 6."""

    if len(peers_raw) % 6 != 0:
        raise ValueError('size of byte_string host/port pairs must be'
                          'a multiple of 6')
    peers = (peers_raw[i:i+6] for i in range(0, len(peers_raw), 6))
    hosts_ports = [(socket.inet_ntoa(peer[0:4]),
                    struct.unpack('!H', peer[4:6])[0]) for peer in peers]
    return hosts_ports
