import struct
from twisted.internet.protocol import Protocol, ClientFactory

ID_TO_MSG = {None: 'keep-alive',
             0: 'choke',
             1: 'unchoke',
             2: 'interested',
             3: 'uninterested',
             4: 'have',
             5: 'bitfield',
             6: 'request',
             7: 'piece',
             8: 'cancel',
             9: 'port'
             }

class PeerProtocol(Protocol):
    '''
    An instance of the BitTorrent protocol. This serves as a client. The
    server is an instance of the ActiveTorrent class (of which this is
    contained within.
    '''

    def __init__(self, client, torrent):
        self.client = client
        self.torrent = torrent
        self.am_choking = 1
        self.am_interested = 0
        self.peer_choking = 1
        self.peer_interested = 0
        self.handshaked = 0
    
    def connectionMade(self):
        self.handshake()
        self.unchoke()
        self.interested()

    def interested(self):
        self.am_interested = 1
        #TODO

    def unchoke(self):
        self.am_choking = 0
        #TODO

    def decode_len_id(self, message):
        len_prefix = struct.unpack_from('!I', message)
        if not len_prefix: #keep alive message, ID is None
            return (0, None)
        else:
            message_id = ord(message[4]) #single byte that must be the 5th byte
            return (len_prefix, message_id)

    def encode_len_id(self, len_prefix, message_id):
        if not len_prefix: #keep alive message
            return '\x00\x00\x00\x00'
        else:
            return struct.pack('!IB', len_prefix, message_id)

    def dataReceived(self, data):
        self.deocde_len_id(data)

    def handshake(self):
        peer_id = self.factory.client.client_id
        info_hash = self.factory.torrent.info_hash
        reserved = '0' * 8
        pstr = 'BitTorrent protocol'
        pstrlen = 68

        #somehow send TODO
        handshake_msg = pstrlen + pstr + reserved + info_hash + peer_id

class PeerProtocolFactory(ClientFactory):
    '''
    Factory to generate instances of the Peer protocol. A Twisted concept.
    '''

    protocol = PeerProtocol

    def __init__(self, client, torrent):
        self.client = client
        self.torrent = torrent

    def clientConnectionLost(self, connector, reason):
        pass
        #need to pass this up to the controlling torrent

    def clientConnectionFailed(self, reason):
        pass
