## BitTorrent Client Implementation

#### Requirements
    * bencode

#### TODO
    * Make announce more robust, several different types of announces
        - maybe separate into a _build_announce method and separate
        implementations
    * Implement the scrape method of a tracker
    * Implement asynchronous downloading with Twisted - look at coroutines
    * Loop through adding each of the files directory from the dict
    * Maintain file mapping
    * Lots of bookeeping to do for protocol implementation.
