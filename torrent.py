#!/usr/bin/env python

import sys
if sys.version_info != (2, 7):
    sys.exit('TwistedTorrent requires Python 2.7')

try:
    import twisted
except ImportError:
    sys.exit('TwistedTorrent requires Twisted')

try:
    import bitarray
except ImportError:
    sys.exit('TwistedTorrent requires bitarray')

if len(sys.argv) == 1:
    sys.exit('Usage: ./torrent.py <list of torrent files>')

from twistedtorrent.client import TorrentClient
TorrentClient(sys.argv[1:])
