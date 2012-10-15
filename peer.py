import socket
import struct

class Peer(object):
    def __init__(self, client, torrent):
        self.client = client
        self.torrent = torrent
        self.ip = '127.0.0.1'
        self.port = 10000
        self.socket = socket.socket()
        try:
            self.socket.connect((self.ip, self.port))
        except socket.error:
            pass

    def encode_prefix_id(self, len_prefix, msg_id):
        return struct.pack('!IB', len_prefix + chr(msg_id))

    def decode_prefix_id(self, message):
        return struct.unpack_from('!IB', message)
