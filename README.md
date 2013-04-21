## TwistedTorrent

A mostly full-featured lightweight BitTorrent client written in Python and
implemented using Twisted.

### Usage

To use TwistedTorrent simply clone the git repo and downlad the necessary packages
and then run (from the top level directory where it is installed):

    ./torrent.py <list of torrents>

### Dependencies

  * Twisted

  * bitarray

### Coming soon

  * The implementation of the Kademlia based Distributed Hash Table (DHT) that is
    used for most torrents nowadays, this includes magnet links.

  * Endgame algorithms and rarity.

#### Resources

[Official BitTorrent Specification](http://wwww.bittorrent.org/beps/bep_0003.html')

[More detailed wiki post on specification](http://wiki.theory.org/BitTorrentSpecification)

[Twisted Docs](http://twistedmatrix.com/documents/current/)
