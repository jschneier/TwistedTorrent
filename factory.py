from bitarray import bitarray
from twisted.internet.protocol import ClientFactory, ServerFactory

from constants import BSIZE
from protocol import PeerProtocol

class PeerProtocolFactory(ClientFactory):
    """Factory to generate instances of the Peer protocol. Maintains state
    data across protocol instances and distributes strategy instructions."""

    protocol = PeerProtocol

    def __init__(self, client, torrent):
        self.client = client
        self.torrent = torrent
        self.protos = set()
        self.bitfield = bitarray(self.torrent.n_pieces * '0', endian='big')
        self.strategy = self.make_requests

    def fetch(self, index, offset, size):
        self.torrent.fetch_block(index, offset, size)

    def add_block(self, index, offset, block):
        self.torrent.add_block(index, offset, block)

    def update_successful_piece(self, index):
        self.bitfield[index] = True
        for proto in self.protos:
            proto.send('have', index=index)

    def make_requests(self):
        for proto in self.protos:
            if len(proto.requests) < 5 and proto.handshaked:
                index, offset_index = self.torrent.next_block()
                offset = offset_index * BSIZE
                length = self.torrent.pieces[index].get_size(offset_index)
                p = (index, offset, length)
                if p not in proto.requests and (proto.peer_bitfield is None or
                                                proto.peer_bitfield[index]):
                    proto.send('request', index=index, offset=offset, length=length)
                    proto.requests.add(p)

    def stop(self):
        """Do nothing because all pieces have been successfully downloaded."""
        pass

class ServerPeerFactory(ServerFactory):
    
    protocol = PeerProtocol
