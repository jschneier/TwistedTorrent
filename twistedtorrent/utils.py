import os
import struct
import socket

def n_random(n):
    """Return a random byte string of length n -- cryptographically secure."""
    return os.urandom(n)

def decode_hosts_ports(peers_raw):
    """Decode a compact byte string of hosts and ports into a list of tuples.
    Peers_raw's length must be a multiple of 6."""

    peers = (peers_raw[i:i+6] for i in range(0, len(peers_raw), 6))
    hosts_ports = [(socket.inet_ntoa(peer[0:4]),
                    struct.unpack('!H', peer[4:6])[0]) for peer in peers]
    return hosts_ports
