import os

def n_random(n):
    """Return a random byte string of length n -- cryptographically secure."""
    return os.urandom(n)
