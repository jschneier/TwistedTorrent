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
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        self.handshaked = False
    
    def connectionMade(self):
        self.handshake()
        self.unchoke()
        self.interested()

    def interested(self):
        self.am_interested = True
        #TODO

    def unchoke(self):
        self.am_choking = False
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
        if not self.handshaked:
            self.decode_handshake(data)
        else:
            self.deocde_len_id(data)

    def handshake(self):
        peer_id = self.factory.client.client_id
        info_hash = self.factory.torrent.info_hash
        reserved = '0' * 8
        pstr = 'BitTorrent protocol'
        pstrlen = 68

        #somehow send TODO
        handshake_msg = pstrlen + pstr + reserved + info_hash + peer_id

    def decode_handshake(self, data):
        '''
        Verify that our peer is sending us a well formed handshake, if not
        we then raise an errback that will close the connection. We can't check
        against peer_id because we set the compact flag in our tracker request.
        If the handshake is well formed we set the handshaked instance variable
        to True so that we know to accept further messages from this peer.
        '''

        if ord(data[0]) != 68:
            #WE NEED TO BREAK OUT TODO, some kind of errback
            pass
        elif data[28:48] != self.factory.torrent.info_hash:
            #WE NEED TO BREAK OUT TODO, some kind of errback
            pass
        elif data[1:20] != 'BitTorrent protocol':
            #WE NEED TO BREAK OUT TODO, some kind of errback
            pass
        self.handshaked = True
            
            

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
