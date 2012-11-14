import struct
from message import Message
from piece import FinalPiece
from bitarray import bitarray
from read_once_buffer import ReadOnceBuffer
from constants import pstr, handshake_len, bsize
from twisted.internet.protocol import Protocol, ClientFactory

DEBUG = True

class PeerProtocol(Protocol):
    """An instance of the BitTorrent protocol. Encapsulates a connection."""

    ID_TO_MSG = {None: 'keep_alive', 0: 'choke', 1: 'unchoke', 2: 'interested',
                 3: 'uninterested', 4: 'have', 5: 'bitfield', 6: 'request',
                 7: 'piece', 8: 'cancel', 9: 'port' }

    def __init__(self):
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        self.handshaked = False
        self.peer_bitfield = None
        self.buf = ReadOnceBuffer()
        self.requests = 0
 
    def connectionMade(self):
        self.send('handshake', info_hash=self.factory.torrent.info_hash,
                                peer_id=self.factory.client.client_id)

    def dataReceived(self, data):
        self.buf += data

        if not self.handshaked:
            if self.bufsize >= handshake_len:
                self.parse_handshake(self.buf[:handshake_len])
                self.send('interested')
            else:
                self.transport.loseConnection()

        while self.bufsize >= 4 and self.has_msg():
            prefix, msg_id, payload = self.parse_message()
            if DEBUG: print 'About to do: %s' % PeerProtocol.ID_TO_MSG[msg_id]
            getattr(self, PeerProtocol.ID_TO_MSG[msg_id])(payload)
            self.factory.make_requests()

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
        return self.bufsize-4 >= struct.unpack('!I', str(self.buf.peek(0, 4)))[0]

    @property
    def bufsize(self):
        return len(self.buf)

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

    def have(self, payload):
        """We only use this if we previously received a bitfield message."""
        if self.peer_bitfield is not None:
            self.peer_bitfield[payload] = True

    def bitfield(self, payload):
        self.peer_bitfield = bitarray(endian='big').frombytes(str(payload))

    def request(self, payload):
        pass 

    def piece(self, payload):
        self.requests -= 1
        index, offset = struct.unpack_from('!II', str(payload))
        block = payload[8:]
        self.factory.add(index, offset, block)

    def cancel(self, payload):
        pass

    def port(self, payload):
        """Not supported"""
        pass

    def parse_message(self):
        prefix, = struct.unpack('!I', str(self.buf[:4]))
        if not prefix: #keep_alive message, ID is None
            return 0, None, None
        else:
            message_id = self.buf[0]
            if message_id < 4:
                return prefix, message_id, None
            else:
                return prefix, message_id, self.buf[0: prefix-1] #-1 for id

    def parse_handshake(self, data):
        """Verify that our peer is sending us a well formed handshake, if not
        we close the connection. If the handshake is well formed we set the
        handshaked instance variable to True so that we know to accept further
        messages from this peer."""

        if data[0] != len(pstr) or data[1:20] != pstr\
            or data[28:48] != self.factory.torrent.info_hash:

            self.transport.loseConnection()
        else:
            self.handshaked = True

    def connectionLost(self, reason):
        self.factory.protos.remove(self)

class PeerProtocolFactory(ClientFactory):
    """Factory to generate instances of the Peer protocol. Maintains state
    data across protocol instances and distributes strategy instructions."""

    protocol = PeerProtocol

    def __init__(self, client, torrent):
        self.client = client
        self.torrent = torrent
        self.protos = []

    def buildProtocol(self, address):
        proto = ClientFactory.buildProtocol(self, address)
        self.protos.append(proto)
        return proto

    def add(self, index, offset, block):
        self.torrent.add_block(index, offset, block)

    def make_requests(self):
        for proto in self.protos:
            if proto.requests < 5 and proto.handshaked: #maybe add handshake and choking data
                index, offset_index = self.torrent.get_block()
                offset = offset_index * bsize
                length = self._get_request_length(index, offset_index)
                if proto.peer_bitfield is not None:
                    if proto.peer_bitfield[index] == True:
                        proto.send('request', index=index, offset=offset, length=length)
                        proto.requests += 1
                else:
                    proto.send('request', index=index, offset=offset, length=length)
                    proto.requests += 1

    def _get_request_length(self, index, offset_index):
        piece = self.torrent.pieces[index]
        if isinstance(piece, FinalPiece) and piece.is_last_block(offset_index):
            return piece.fsize
        else:
            return bsize

    @property
    def connections(self):
        return len(self.protos)
