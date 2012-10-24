## BitTorrent Client Implementation

#### Requirements
    * bencode
    * Twisted

#### TODO
    * Fix sending (message class) piece method
    * Add hash verification of the pieces -- IMPORTANT
    * Pass things up through the factory
    * Implement asynchronous downloading with Twisted
    * Lots of bookeeping to do for protocol implementation
    * Implement the scrape method of a tracker

#### Resources

[Official BitTorrent Specification](http://wwww.bittorrent.org/beps/bep_0003.html')

[More detailed wiki post on specification](http://wiki.theory.org/BitTorrentSpecification)

[Twisted Docs](http://twistedmatrix.com/documents/current/)
