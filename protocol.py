import struct
from bitarray import bitarray
from twisted.internet.protocol import Protocol

from message import Message
from read_once_buffer import ReadOnceBuffer
from constants import PSTR, HANDSHAKE_LEN, MAX_SIZE

class PeerProtocol(Protocol):
    """An instance of the BitTorrent protocol. Encapsulates a connection."""

    id_to_msg = {None: 'keep_alive', 0: 'choke', 1: 'unchoke', 2: 'interested',
                 3: 'uninterested', 4: 'have', 5: 'bitfield', 6: 'request',
                 7: 'piece', 8: 'cancel', 9: 'port', 13: 'suggest_piece',
                 14: 'have_all', 15: 'have_none', 16: 'reject_request',
                 17: 'allowed_fast'}

    extension_ids = frozenset((13, 14, 15, 16, 17))

    def __init__(self):
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        self.handshaked = False
        self.fast_extension = False
        self.peer_bitfield = None
        self.buf = ReadOnceBuffer()
        self.requests = set()

    def connectionMade(self):
        self.send('handshake', info_hash=self.factory.torrent.info_hash,
                                peer_id=self.factory.client.client_id)
        self.factory.protos.add(self)
    def dataReceived(self, data):
        self.buf += data

        if not self.handshaked:
            if self.bufsize >= HANDSHAKE_LEN:
                self.parse_handshake(self.buf[:HANDSHAKE_LEN])

                if all(self.factory.bitfield) and self.fast_extension:
                    self.send('have_all')
                elif not any(self.factory.bitfield) and self.fast_extension:
                    self.send('have_none')
                else:
                    self.send('bitfield', bitfield=self.factory.bitfield)

                self.send('interested')
            else:
                self.transport.loseConnection()

        while self.has_msg():
            prefix, msg_id, payload = self.parse_message()
            if msg_id in self.extension_ids and not self.fast_extension:
                self.transport.loseConnection()
                break

            getattr(self, self.id_to_msg[msg_id])(payload)
            self.factory.strategy()

    def send(self, mtype, **kwargs):
        """Send a message to our peer, also take care of state that determines
        who is choking who and who is interested."""

        self.transport.write(Message(mtype, **kwargs))

        if mtype == 'interested':
            self.am_interested = True
        elif mtype == 'not_interested':
            self.am_interested = False
        elif mtype == 'choke':
            self.am_choking = True
        elif mtype == 'unchoke':
            self.am_choking = False

    def has_msg(self):
        """Check if there is a full message to pull off, first 4 bytes
        determine the necessary length and are not included in calc."""
        return self.bufsize >= 4 and self.bufsize - 4 >= struct.unpack('!I', str(self.buf.peek(0, 4)))[0]

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
        if self.peer_bitfield is None:
            self.peer_bitfield = bitarray(self.torrent_size * '0', endian='big')
        self.peer_bitfield[struct.unpack('!I', str(payload))[0]] = True

    def bitfield(self, payload):
        self.peer_bitfield = bitarray(endian='big')
        self.peer_bitfield.frombytes(str(payload))

    def request(self, payload):
        index, offset, size = struct.unpack('!III', payload)
        if size > MAX_SIZE:
            self.transport.loseConnection()
        if self.factory.bitfield[index]:
            block = self.factory.fetch(index, offset, size)
            self.send('piece', index=index, offset=offset, block=block)

    def piece(self, payload):
        index, offset = struct.unpack_from('!II', str(payload))
        block = payload[8:]
        self.requests.remove((index, offset, len(block)))
        self.factory.add_block(index, offset, block)

    def cancel(self, payload):
        pass

    def port(self, payload):
        """Not supported"""
        pass

    def suggest_piece(self, payload):
        index = struct.unpack('!I', payload)
        if not self.factory.bitfield[index]:
            pass  # TODO

    def allowed_fast(self, payload):
        pass  # TODO

    def have_all(self, *args):
        self.peer_bitfield = bitarray(self.torrent_size * '1', endian='big')

    def have_none(self, *args):
        self.peer_bitfield = bitarray(self.torrent_size * '0', endian='big')

    def reject_request(self, payload):
        index, offset, length = struct.unpack('!III', str(payload))
        self.requests.remove((index, offset, length))

    def parse_message(self):
        prefix, = struct.unpack('!I', str(self.buf[:4]))
        if not prefix:  # keep_alive message, ID is None
            return 0, None, None

        message_id = self.buf[0]
        if message_id < 4:
            return prefix, message_id, None
        else:
            return prefix, message_id, self.buf[0: prefix-1]  # -1 for id

    def parse_handshake(self, data):
        """Verify that our peer is sending us a well formed handshake, if not
        we close the connection. If the handshake is well formed we set the
        handshaked instance variable to True so that we know to accept further
        messages from this peer. We also decode which extensions both us and
        our peer support."""

        if (data[0] != len(PSTR) or data[1:20] != PSTR
            or data[28:48] != self.factory.torrent.info_hash):

            self.transport.loseConnection()
        else:
            self.handshaked = True

        reserved = data[20:28]
        if reserved[7] & ord('\x04'):
            self.fast_extension = True

    def connectionLost(self, reason):
        self.factory.protos.remove(self)

    @property
    def torrent_size(self):
        return self.factory.torrent.n_pieces

    @property
    def bufsize(self):
        return len(self.buf)
