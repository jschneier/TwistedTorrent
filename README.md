## BitTorrent Client Implementation

#### Requirements
    * bencode
    * Twisted
    * bitarray

#### TODO
    * Make a request class so I can time them out
    * Each protocol instances should have a maximum number of requests out
    * Implement cancel method
    * Add a bitfield parameter that we send
    * Implement numerous strategies
    * Track download progress
    * Write front end command line layer
    * Write tests to verify
    * Would be nice - write out bencode (maybe not necessary)

#### Resources

[Official BitTorrent Specification](http://wwww.bittorrent.org/beps/bep_0003.html')

[More detailed wiki post on specification](http://wiki.theory.org/BitTorrentSpecification)

[Twisted Docs](http://twistedmatrix.com/documents/current/)
