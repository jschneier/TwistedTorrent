import struct

from .constants import PSTR, RESVD

class Message(str):
    """Dyanmically generate the string (bytes) which are sent across the wire.
    Have to hijack object creation with __new__ since strings are immutable and
    by the time we get to __init__ it is too late."""

    def __new__(cls, mtype, **kwargs):
        return str.__new__(cls, getattr(cls, mtype)(**kwargs))

    @staticmethod
    def handshake(**kwargs):
        length = chr(len(PSTR))
        resvd = RESVD
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
        return struct.pack('!IBI', 5, 4, kwargs['index'])

    @staticmethod
    def bitfield(**kwargs):
        bitfield = kwargs['bitfield'].tobytes()
        length = len(bitfield)
        header = struct.pack('!IB', length + 1, 5)
        return header + bitfield

    @staticmethod
    def request(**kwargs):
        return struct.pack('!IBIII', 13, 6, kwargs['index'],
                                kwargs['offset'], kwargs['length'])

    @staticmethod
    def piece(**kwargs):
        block = kwargs['block'].tobytes()
        length = len(block)
        header = struct.pack('!IBII', length + 9, 7,
                                kwargs['index'], kwargs['offset'])
        return header + block

    @staticmethod
    def cancel(**kwargs):
        return struct.pack('!IBIII', 13, 8, kwargs['index'],
                                kwargs['offset'], kwargs['length'])

    @staticmethod
    def port(**kwargs):
        return struct.pack('!IBH', 3, 9, kwargs['listen_port'])

    # from here on down are fast peers extensions
    @staticmethod
    def suggest_piece(**kwargs):
        return struct.pack('!IBI', 5, 13, kwargs['index'])

    @staticmethod
    def have_all(**kwargs):
        return struct.pack('!IB', 1, 14)

    @staticmethod
    def have_none(**kwargs):
        return struct.pack('!IB', 1, 15)
 
    @staticmethod
    def reject_request(**kwargs):
        return struct.pack('!IBIII', 13, 16, kwargs['index'],
                                kwargs['offset'], kwargs['length'])

    @staticmethod
    def allowed_fast(**kwargs):
        return struct.pack('!IBI', 5, 17, kwargs['index'])
