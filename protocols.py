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

    def __init__(self, client, torrent):
        self.client = client
        self.torrent = torrent
        self.am_choking = 1
        self.am_interested = 0
        self.peer_choking = 1
        self.peer_interested = 0
    
    def connectionMade(self):
        self.handshake()

    def decode_len(self, message):
        return struct.unpack_from('!I', message)

    def is_keep_alive(self, message):
        return not bool(self.decode_len(message))

    def dataReceived(self, data):
        self.deocde_len(data)

    def handshake():
        pass

class PeerProtocolFactory(ClientFactory):

    protocol = PeerProtocol

    def clientConnectionLost(self, connector, reason):
        pass
        #need to pass this up to the controlling torrent

    def clientConnectionFailed(self, reason):
        pass
