class BTDecodeError(Exception):
    pass

class BTEncodeError(Exception):
    pass

def decode_string(s, start):
    colon = s.find(':', start)
    length = int(s[start:colon])
    end = colon + length + 1
    return s[colon + 1:end], end

def decode_int(s, start):
    end = s.find('e', start)
    if s[start+1] == '0' and end != start+2:
        raise ValueError
    return int(s[start + 1:end]), end + 1

def decode_list(s, start):
    start += 1
    ret = []
    while s[start] != 'e':
        ans, end = func(s, start)
        ret.append(ans)
        start = end
    return ret, start + 1

def decode_dict(s, start):
    start += 1
    ret = {}
    while s[start] != 'e':
        key, end = decode_string(s, start)
        start = end
        value, end = func(s, start)
        ret[key] = value
        start = end
    return ret, start + 1

'''
If the character at position start is in 0-9 True the or will short circuit and
True will be returned, at which point the results of decode_string will be
returned; otherwise the or will return the character at position start and the
appropriate function from decoders will be called.
'''
func = lambda s, start: decoders[s[start].isdigit() or s[start]](s, start)
decoders = {'i': decode_int, 'l': decode_list,
            'd': decode_dict, True: decode_string}

def btdecode(s):
    try:
        ret, length = func(s, 0)
    except (KeyError, IndexError, TypeError, ValueError):
        raise BTDecodeError('Invalid bencoded string')
    if len(s) != length:
        raise BTDecodeError('Extraneous data after bencoded string')
    return ret

def encode_string(s):
    return str(len(s)) + ':' + s

def encode_int(i):
    return 'i' + str(i) + 'e'

def encode_list(l):
    return 'l' + ''.join(encoders[type(i)](i) for i in l) + 'e'

def encode_dict(d):
    keys = sorted(d)
    enc_keys = [encode_string(key) for key in keys]
    enc_vals = [encoders[type(d[key])](d[key]) for key in keys]
    return 'd' + ''.join(''.join(p) for p in zip(enc_keys, enc_vals)) + 'e'

def btencode(stuff):
    try:
        ret = encoders[type(stuff)](stuff)
    except KeyError:
        raise BTDecodeError('Not valid type for bencoding')
    return ret

encoders = {dict: encode_dict, list: encode_list,
            str: encode_string, int: encode_int}
