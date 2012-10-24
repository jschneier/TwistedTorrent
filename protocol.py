import struct
from message import Message
from constants import pstr, handshake_len
from read_once_buffer import ReadOnceBuffer
from twisted.internet.protocol import Protocol, ClientFactory

DEBUG = True
class PeerProtocol(Protocol):
    """An instance of the BitTorrent protocol. This serves as a client."""

    def __init__(self):
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        self.handshaked = False
        self.timer = None
        self.buf = ReadOnceBuffer()
 
    def connectionMade(self):
        if DEBUG: print 'Successfully connected, sending handshake'
        self.send('handshake', info_hash= self.factory.torrent.info_hash,
                                peer_id = self.factory.client.client_id)

    def dataReceived(self, data):
        self.buf += data
        if DEBUG: print 'Data Received', repr(data)
        if DEBUG: print 'Total Data', repr(self.buf)

        if not self.handshaked:
            if self.bufsize >= handshake_len:
                if DEBUG: print 'Received handshake, parsing'
                self.parse_handshake(self.buf[:handshake_len])
                if DEBUG: print 'Parsed handshake, sending interested'
                self.send('interested')
            else:
                if DEBUG: print 'Incomplete handshake received, losing conn'
                self.transport.loseConnection()

        if DEBUG: print 'Other data received:', repr(data)
        if self.bufsize >= 4:
            while self.has_msg():
                prefix, msg_id, payload = self.parse_message()

    def send(self, mtype, **kwargs):
        """Send a message to our peer, also take care of state that determines
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

    def has_msg(self):
        """Check if there is a full message to pull off, first 4 bytes
        determine the necessary length and are not included in calc."""
        return self.bufsize-4 >= struct.unpack('!I', (self.buf.peek(0, 4)))

    @property
    def bufsize(self):
        return len(self.buf)

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

    def have(self, prefix, payload):
        pass

    def bitfield(self, prefix, payload):
        '''Optional so we ignore it.'''
        pass

    def request(self, prefix, payload):
        pass 

    def piece(self, prefix, payload):
        block_len = prefix - 9
        index = chr(payload[0])
        begin = chr(payload[1])
        block = payload[2:]
        self.factory.add(block_len, index, begin, block)

    def cancel(self, prefix, payload):
        #TODO
        pass

    def port(self, prefix, payload):
        '''Not supported'''
        pass

    def parse_message(self, message):
        prefix = struct.unpack_from('!I', message)
        if not prefix: #keep alive message, ID is None
            return 0, None, None
        else:
            message_id = ord(message[4])
            if message_id < 4:
                return prefix, message_id, None
            else:
                return prefix, message_id, message[5:]

    def parse_handshake(self, data):
        """
        Verify that our peer is sending us a well formed handshake, if not
        we then raise an exception that will close the connection.  If the
        handshake is well formed we set the handshaked instance variable
        to True so that we know to accept further messages from this peer.
        """

        if DEBUG: print 'Handshake being parsed'

        if ord(data[0]) != len(pstr) or data[1:20] != pstr\
            or data[28:48] != self.factory.torrent.info_hash:

            if DEBUG: print 'Bad handhsake, losing connection'
            self.transport.loseConnection()
        else:
            self.handshaked = True
            if DEBUG: print 'Handshake successfully parsed'

class PeerProtocolFactory(ClientFactory):
    """
    Factory to generate instances of the Peer protocol. Maintains state data
    across protocol instances.
    """

    protocol = PeerProtocol

    def __init__(self, client, torrent):
        self.client = client
        self.torrent = torrent

    def clientConnectionLost(self, connector, reason):
        pass
        #need to pass this up to the controlling torrent

    def clientConnectionFailed(self, connector, reason):
        pass
