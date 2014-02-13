class TorrentException(Exception):
    """Base class of all torrent exceptions."""

class NoValidTorrent(TorrentException):
    """Raised when the client didn't receive any valid torrents to process."""

class AnnounceError(TorrentException):
    """Raised during the announce flow with a tracker."""
