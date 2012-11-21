import struct
from constants import PSTR

class Message(str):
    """Subclassing of string, hijack the constructor with __new__ because
    strings are otherwise immutable."""

    def __new__(cls, mtype, **kwargs):
        return str.__new__(cls, getattr(cls, mtype)(**kwargs))

    @staticmethod
    def handshake(**kwargs):
        length = chr(len(PSTR))
        resvd = chr(0) * 8
        return ''.join([length, PSTR, resvd,
                        kwargs['info_hash'], kwargs['peer_id']])

    @staticmethod
    def keep_alive(**kwargs):
        return struct.pack('!I', 0)

    @staticmethod
    def choke(**kwargs):
        return struct.pack('!IB', 1, 0)

    @staticmethod
    def unchoke(**kwargs):
        return struct.pack('!IB', 1, 1)

    @staticmethod
    def interested(**kwargs):
        return struct.pack('!IB', 1, 2)

    @staticmethod
    def not_interested(**kwargs):
        return struct.pack('!IB', 1, 3)

    @staticmethod
    def have(**kwargs):
        return struct.pack('!IBI', 5, 4, kwargs['piece_index'])

    @staticmethod
    def bitfield(**kwargs):
        length = len(kwargs['bitfield'])
        arg = Message._make_struct_arg('!IB', length)
        return struct.pack(arg, length + 1, 5, kwargs['bitfield'])

    @staticmethod
    def request(**kwargs):
        return struct.pack('!IBIII', 13, 6, kwargs['index'],
                                kwargs['offset'], kwargs['length'])

    @staticmethod
    def piece(**kwargs):
        length = len(kwargs['block'])
        arg = Message._make_struct_arg('!IBII', length)
        return struct.pack(arg, length + 9, 7, kwargs['index'],
                                kwargs['offset'], kwargs['block'])

    @staticmethod
    def cancel(**kwargs):
        return struct.pack('!IBIII', 13, 8, kwargs['index'],
                                kwargs['offset'], kwargs['length'])

    @staticmethod
    def port(**kwargs):
        return struct.pack('!IBH', 3, 9, kwargs['listen-port'])

    @staticmethod
    def _make_struct_arg(base, length):
        """Variable length messages need struct args dynamically created."""
        struct_string = base + 'I' * length / 4
        remainder = length % 4
        if remainder:
            print 'Shit, non-packed bytes wanted for message'
        return struct_string
