import struct

class Message(object):
    '''
    Class to wrap up the ugliness of the nitty gritty implementation of the
    protocol. Message objects do not persist for very long.
    '''

    ID_TO_MSG = { None: 'keep_alive',
                  0: 'choke',
                  1: 'unchoke',
                  2: 'interested',
                  3: 'uninterested',
                  4: 'have',
                  5: 'bitfield',
                  6: 'request',
                  7: 'piece',
                  8: 'cancel',
                  9: 'port',
                  }
    
    def __init__(self, msg_id, payload, **kwargs):
        getattr(self, Message.ID_TO_MSG[msg_id])(msg_id, payload, **kwargs)

    def choke(self, *args):
        return struct.pack
