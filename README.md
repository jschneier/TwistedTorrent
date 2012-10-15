## BitTorrent Client Implementation

#### Requirements
    * bencode

#### TODO
    * Make announce more robust, several different types of announces
        - maybe separate into a _build_announce method and separate
        implementations
    * Figure out if we need to write our own protocol
    * Implement the scrape method of a tracker
    * Figure out how to connect to peers
    * Implement asynchronous downloading with Twisted - look at coroutines
    * Loop through adding each of the files directory from the dict
    * Maintain file mapping
