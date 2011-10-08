# -*- coding: utf-8 -*-
import string
# import random
import time
#tretiy4
__ALPHABET = string.digits + 'abcdef'#u'абвгдежзиклмнопрстуфхцчшщыэюя'#string.ascii_lowercase
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
    # tretiy3
    # while len(s) < __MAXLEN:
    #     s.append('0')
    return ''.join(reversed(s))

def decode_id(s):
    n = 0
    for c in s.lstrip('0'):
        n = n * __BASE + __ALPHABET_REVERSE[c]
    return n

def gen_id():
    return encode_id(int(round((time.time() - 41*365*24*60*60 - 270*24*60*60))*100))
    # tretiy3
    # 41 year from epoch to 01.01.2011 and 270 days to launch
    # return encode_id(random.randint(0,__MAX))

if __name__ == '__main__':
    print gen_id()
    # int_uuid = int(round((time.time() - 41*365*24*60*60 - 270*24*60*60))*100)
    # print int_uuid
    # print 'encode'
    # encoded = encode_id(int_uuid)
    # print encoded
    # print len(str(encoded))
    # print 'decode'
    # decoded = decode_id(encoded)
    # print "final id"
    # print decoded#"%0.2X" % decoded

    
