import struct
from constants import pstr
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
        if DEBUG: print 'Data Received', repr(data)
        if DEBUG: print 'Total Data', repr(self.data_buffer)

        if not self.handshaked:
            if DEBUG: print 'Received handshake, decoding'
            self.decode_handshake(data)
            if DEBUG: print 'Decoded handshake, sending interested'
            self.send('interested')
        else:
            if DEBUG: print 'Other data received:', repr(data)
            len_prefix, msg_id, payload = self.decode_message(data)

    def send(self, mtype, **kwargs):
        """Send a message to our peers, also take care of state that determines
        who is choking who and who is interested."""

        self.transport.write(Message(mtype, **kwargs))

        if mtype == 'interested':
            self.am_interested = True
        elif mtype == 'not_interested':
            self.am_interested = False
        elif mtype == 'choke':
            self.peer_choking = True
        elif mtype == 'unchoke':
            self.peer_choking = False

    @property
    def bufsize(self):
        return len(self.data_buffer)

    def keep_alive(self, *args):
        #TODO: reset timer
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

    def decode_handshake(self, data):
        """
        Verify that our peer is sending us a well formed handshake, if not
        we then raise an exception that will close the connection.  If the
        handshake is well formed we set the handshaked instance variable
        to True so that we know to accept further messages from this peer.
        """

        if DEBUG: print 'Handshake being decoded'

        try:
            if ord(data[0]) != len(pstr) or data[1:20] != pstr\
                or data[28:48] != self.factory.torrent.info_hash:

                if DEBUG: print 'Bad handhsake, losing connection'
                self.transport.loseConnection()
        except IndexError:
            if DEBUG: print 'Incomplete data: trying again later'
        else:
            self.handshaked = True
            if DEBUG: print 'Handshake successfully decoded'

class PeerProtocolFactory(ClientFactory):
    """
    Factory to generate instances of the Peer protocol. Maintains state data
    across protocol instances.
    """

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
