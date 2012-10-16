import sys
import time
import urllib
import hashlib
import bencode

class Torrent(object):
    '''
    Container for parsed metadata from a .torrent file.
    '''
 
    def __init__(self, filename):
        self.filename = filename
        self.parse_metainfo()

    def parse_metainfo(self):
        torrent_dict = bencode.bdecode(open(self.filename).read())

        self.announce_url = torrent_dict['announce']
        self.info = torrent_dict['info']
        self.info_hash = hashlib.sha1(bencode.bencode(self.info)).digest()
        self.piece_length = self.info['piece length']

        #break string pieces up into a list of those pieces
        pieces_string = self.info['pieces']
        self.pieces = [pieces_string[i:i+20]
                        for i in xrange(0, len(pieces_string), 20)]

        self.num_files = len(self.info['files']) if 'files' in self.info else 1
        if self.num_files == 1:
            self.length = self.info['length']
            self.names = [self.info['name']] #make it a list so we can iterate
        else:
            self.length = sum(f['length'] for f in self.info['files'])
            self.names = [f['path'][0] for f in self.info['files']]

class ActiveTorrent(Torrent):
    '''
    Represents a torrent that is in the process of being downloaded.
    '''
    
    def __init__(self, filename):
        super(ActiveTorrent, self).__init__(filename)
        self.uploaded = 0
        self.downloaded = 0
        #self.index_pieces = {index: (piece, 0) for index, piece in
        #                        enumerate(self.pieces)}
        self.peers = []

    @property
    def left(self):
        return self.length - self.downloaded

    @property
    def connections(self):
        return len(self.peers)

    def connect_to_peer(self, (host, port)):
        from twisted.internet import reactor
        #TODO: connect the higher end to the lower end
        reactor.connectTCP(host, port, factory)

class AnnounceError(Exception):
    pass

class TorrentClient(object):
    '''
    A torrent client object, makes the request to the tracker as specified 
    and then connects to each peer as necessary.
    '''

    def __init__(self, **kwargs):
        self.client_id = (str(time.time()) + '901asdf0293fasljz23raasd')[:20]
        self.port = 6881
        self.torrents = []

    def add_torrent(self, torrent):
        self.torrents.append(torrent)
        host_ports = torrent.announce(torrent)
        for host_port in host_ports:
            torrent.connect_to_peer(host_port)

    def announce(self, torrent):
        '''
        Create the url to send to the tracker, parse the response and then
        generate the host and ports of the specified peers.
        '''

        announce_query = {
            'info_hash': torrent.info_hash,
            'peer_id': self.client_id,
            'port': self.port,
            'uploaded': torrent.uploaded,
            'downloaded': torrent.downloaded,
            'left': torrent.left,
            'event': 'started', #TODO: some way to determine what event
        }

        base = torrent.announce_url
        url = base + '?' + urllib.urlencode(announce_query)

        response = urllib.urlopen(url).read()
        if not response:
            raise AnnounceError('No response from tracker for url %s' % url)

        tracker_dict = bencode.bdecode(response)

        if 'failure reason' in tracker_dict:
            raise AnnounceError('''failure reason key in tracker response\
                                    %s:''' % tracker_dict['failure reason'])

        peers_raw = tracker_dict['peers']
        if isinstance(peers_raw, dict):
            raise AnnounceError('peers as dictionary model not implemented')

        peers_bytes = (peers_raw[i:i+6] for i in range(0, len(peers_raw), 6))
        peers = (map(ord, peer) for peer in peers_bytes)
        host_ports = [('.'.join(map(str, peer[0:4])), 256 * peer[4] + peer[5]) for peer in peers]

        return host_ports

if __name__ == '__main__':
    client = TorrentClient()
    torrent = ActiveTorrent(sys.argv[1])
    client.announce(torrent)
