def do_torrent():
    import sys
    from twistedtorrent.client import TorrentClient
    if len(sys.argv == 1):
        sys.exit('Usage: torrent <list of torrent files>')
    TorrentClient(sys.argv[1:])
