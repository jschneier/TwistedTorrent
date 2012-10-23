import struct
from message import Message
from twisted.internet.protocol import Protocol, ClientFactory

DEBUG = True

class HandshakeException(Exception):
    pass

class PeerProtocol(Protocol):
    """An instance of the BitTorrent protocol. This serves as a client."""

    def __init__(self):
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        self.handshaked = False
        self.timer = None
        self.data_buffer = bytearray()
 
    def connectionMade(self):
        if DEBUG: print 'Successfully connected, sending handshake'
        self.send('handshake', info_hash= self.factory.torrent.info_hash,
                                peer_id = self.factory.client.client_id)

    def dataReceived(self, data):
        self.data_buffer += data
        if DEBUG: print 'Data Received'
        if not self.handshaked:
            if DEBUG: print 'Received handshake, decoding', repr(data)
            self.decode_handshake(data)
            if DEBUG: print 'Decoded handshake, seding interested and unchoke'
        else:
            if DEBUG: print 'Other data received:', repr(data)
            len_prefix, msg_id, payload = self.decode_message(data)

    def keep_alive(self, *args):
        pass

    def choke(self, *args):
        self.peer_choking = True

    def unchoke(self, *args):
        self.peer_choking = False

    def interested(self, *args):
        self.peer_interested = True

    def uninterested(self, *args):
        self.peer_interested = False

    def have(self, len_prefix, payload):
        pass

    def bitfield(self, len_prefix, payload):
        '''Optional so we ignore it.'''
        pass

    def request(self, len_prefix, payload):
        pass 

    def piece(self, len_prefix, payload):
        block_len = len_prefix - 9
        index = chr(payload[0])
        begin = chr(payload[1])
        block = payload[2:]
        self.factory.add(block_len, index, begin, block)

    def cancel(self, len_prefix, payload):
        #TODO
        pass

    def port(self, len_prefix, payload):
        '''Not supported'''
        pass

    def decode_message(self, message):
        len_prefix = struct.unpack_from('!I', message)
        if not len_prefix: #keep alive message, ID is None
            return 0, None, None
        else:
            message_id = ord(message[4]) #single byte that must be the 5th byte
            if message_id < 4:
                return len_prefix, message_id, None
            else:
                return len_prefix, message_id, message[5:]

    def encode_len_id(self, len_prefix, message_id):
        if not len_prefix: #keep alive message
            return '\x00\x00\x00\x00'
        else:
            return struct.pack('!IB', len_prefix, message_id)

    def handshake(self):
        peer_id = self.factory.client.client_id
        info_hash = self.factory.torrent.info_hash
        reserved = chr(0) * 8
        pstr = 'BitTorrent protocol'
        pstrlen = chr(len(pstr))

        handshake_msg = pstrlen + pstr + reserved + info_hash + peer_id
        self.transport.write(handshake_msg)

    def decode_handshake(self, data):
        """
        Verify that our peer is sending us a well formed handshake, if not
        we then raise an exception that will close the connection. We can't
        check against peer_id because we set the compact flag in our tracker request.
        If the handshake is well formed we set the handshaked instance variable
        to True so that we know to accept further messages from this peer.
        """

        if DEBUG: print 'Handshake being decoded'

        try:
            if ord(data[0]) != 19 or data[1:20] != 'BitTorrent protocol'\
                or data[28:48] != self.factory.torrent.info_hash:
                if DEBUG: print 'Bad handhsake, losing connection'
                self.transport.loseConnection()
        except IndexError:
            self.transport.loseConnection()
        else:
            self.handshaked = True

        if DEBUG: print 'Handshake successfully decoded'

    def self_choke(self):
        self.transport.write(struct.pack('!IB', 1, 0))
        self.am_choking = True

    def self_unchoke(self):
        self.transport.write(struct.pack('!IB', 1, 1))
        self.am_choking = False

    def self_interested(self):
        self.transport.write(struct.pack('!IB', 1, 2))
        self.am_interested = True

    def self_uninterested(self):
        self.transport.write(struct.pack('!IB', 1, 3))
        self.am_interested = False

class PeerProtocolFactory(ClientFactory):
    """Factory to generate instances of the Peer protocol."""

    protocol = PeerProtocol

    def __init__(self, client, torrent):
        self.client = client
        self.torrent = torrent
        self.bufsize = 0
        self.buffer = []

    def add(self, block_len, index, begin, block):
        self.bufsize += block_len

    def clientConnectionLost(self, connector, reason):
        pass
        #need to pass this up to the controlling torrent

    def clientConnectionFailed(self, connector, reason):
        pass
