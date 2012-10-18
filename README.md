## BitTorrent Client Implementation

#### Requirements
    * bencode
    * Twisted

#### TODO
    * Add hash verification of the pieces -- IMPORTANT
    * Add disconnection
    * Pass things up through the factory
    * Grok choking
    * Implement asynchronous downloading with Twisted
    * Loop through adding each of the files directory from the dict
    * Lots of bookeeping to do for protocol implementation
    * Implement the scrape method of a tracker
    * Refactor the protocol

#### Resources

[Official BitTorrent Specification](http://wwww.bittorrent.org/beps/bep_0003.html')

[More detailed wiki post on specification](http://wiki.theory.org/BitTorrentSpecification)

[Twisted Docs](http://twistedmatrix.com/documents/current/)
