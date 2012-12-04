#!/usr/bin/env python

import sys
VERSION = sys.version_info
if VERSION[0] != 2 or VERSION[1] != 7:
    sys.exit('TwistedBits requires Python 2.7')

try:
    import twisted
except ImportError:
    sys.exit('TwistedBits requires Twisted')

try:
    import bitarray
except ImportError:
    sys.exit('TwistedBits requires bitarray')

if len(sys.argv) == 1:
    sys.exit('Usage: ./torrent.py <list of torrent files>')

from twistedbits.client import TorrentClient
TorrentClient(sys.argv[1:])
