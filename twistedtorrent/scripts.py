def torrent():
    import sys
    from twistedtorrent import TorrentClient
    if len(sys.argv) == 1:
        sys.exit('Usage: torrent <list of torrent files>')
    TorrentClient(sys.argv[1:])
