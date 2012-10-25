## BitTorrent Client Implementation

#### Requirements
    * bencode
    * Twisted

#### TODO
    * Implement a strategy for requesting pieces, test that it works
    * Think hard about where I want factory and ActiveTorrent to separate
    * Implement torrent stopping itself, clean up extraneous references
    * Refactor code, I feel as though there are many code smells throughout
    * Reevaluate data structure
    * Implement the scrape method of a tracker

#### Resources

[Official BitTorrent Specification](http://wwww.bittorrent.org/beps/bep_0003.html')

[More detailed wiki post on specification](http://wiki.theory.org/BitTorrentSpecification)

[Twisted Docs](http://twistedmatrix.com/documents/current/)
