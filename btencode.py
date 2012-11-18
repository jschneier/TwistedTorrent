'''
string: number -> take off ':', take off number
integer: i ... e where ... is any number of chars, including a -
list: l ... e where ... is any number of other bencoded values
dict: d b_string b_ele e
'''

def decode_string(s, start):
    colon = s.find(':', start)
    length = int(s[:colon])
    return (s[colon+1: colon+length+1], start+colon+length+1)

def decode_int(s, start):
    e_ind = s.find('e', start)
    if s[1] == '0' and e_ind != 2:
        raise ValueError
    return (int(s[1:e_ind]), e_ind + start)

def decode_list(s, start):
    start += 1
    ret = []
    while s[start] != 'e':
        ans, end = bdecode(s[start:], start)
        ret.append(ans)
        start = end
    return ret

def decode_dict(s, start):
    pass

decoders = {'i': decode_int, 'l': decode_list,
            'd': decode_dict, True: decode_string}

def bdecode(s, start):
    if not s:
        return
    else:
        return decoders[s[0].isdigit() or s[0]](s, start)
