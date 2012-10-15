from twisted.internet.protocol import Protocol, ClientFactory

class PeerProtocol(Protocol):

    def __init__(self):
        pass
    
    def connectionMade(self):
        self.handshake()

    def dataReceived(self, data):
        self.factory.deocde(data)

    def handshake():
        pass

class PeerProtocolFactory(ClientFactory):

    protocol = PeerProtocol

    def clientConnectionLost(self, connector, reason):
        pass
        #need to pass this up to the controlling torrent

    def clientConnectionFailed(self, reason):
        pass
