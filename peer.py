class Peer(object):
    '''A single peer connection for a particular torrent'''

    def __init__(self, client, torrent, (ip, port)):
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        self.ip, self.port = (ip, port)

    def handshake(self):
        pass 
