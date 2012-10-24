pstr = 'BitTorrent protocol'
handshake_len = 68
block_size = 16384 # 2**14
sum_bytes = lambda bytes: sum(ord(byte) for byte in bytes)
