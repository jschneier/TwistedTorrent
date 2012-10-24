import struct
from constants import pstr

class Message(str):
    """Subclassing of string, hijack the constructor with __new__ because
    strings are otherwise immutable."""

    def __new__(cls, mtype, **kwargs):
        return str.__new__(cls, getattr(cls, mtype)(**kwargs))

    @staticmethod
    def handshake(**kwargs):
        length = chr(len(pstr))
        resvd = chr(0) * 8
        return length + pstr + resvd + kwargs['info_hash'] + kwargs['peer_id']

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
        return struct.pack('!IBI', kwargs['length'], 5, kwargs['bitfield'])

    @staticmethod
    def request(**kwargs):
        return struct.pack('!IBIII', 13, 6, kwargs['index'],
                                kwargs['begin'], kwargs['length'])

    @staticmethod
    def piece(**kwargs):
        return struct.pack('!IBIII', kwargs['length'], 7, kwargs['index'],
                                kwargs['begin'], kwargs['block'])

    @staticmethod
    def cancel(**kwargs):
        return struct.pack('!IBIII', 13, 8, kwargs['index'],
                                kwargs['begin'], kwargs['length'])

    @staticmethod
    def port(**kwargs):
        return struct.pack('!IBH', 3, 9, kwargs['listen-port'])

    @staticmethod
    def make_struct_arg(length):
        """Variable length messages need struct args dynamically created."""

        num_i = length / 4
