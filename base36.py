import string
import random

__ALPHABET = string.digits + string.ascii_lowercase
__ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(__ALPHABET))
__BASE = len(__ALPHABET)
__MAX = 18446744073709551615L
__MAXLEN = 13

def encode_id(n):
    s = []
    while True:
        n, r = divmod(n, __BASE)
        s.append(__ALPHABET[r])
        if n == 0: break
    while len(s) < __MAXLEN:
        s.append('0')
    return ''.join(reversed(s))

def decode_id(s):
    n = 0
    for c in s.lstrip('0'):
        n = n * __BASE + __ALPHABET_REVERSE[c]
    return n

def gen_id():
    return encode_id(random.randint(0,__MAX))

if __name__ == '__main__':
    print 'init'
    uuid = '6e8cd405e6a86ae6f5fda9058600a2ea' 
    print uuid
    int_uuid = int(uuid, 16)
    print int_uuid
    print 'encode'
    encoded = encode_id(int_uuid)
    print encoded
    print 'decode'
    decoded = decode_id(encoded)
    print "final id"
    print "%0.2X" % decoded
    

    
    # "%0.2X" % 146946301434897565240793065095149167338L
    
