# -*- coding: utf-8 -*-
words = [u'компьютер',u'интернет',u'магазин',u'купить',u'калининград',u'техника']

def makeCombinations():
    base = len(words)
    cycle=0
    while cycle<len(words):
        cycle+=1
        for a in xrange(base):
            print "?----------------------------"
            keys = []
            for b in xrange(a):
                keys.append(words[b])
            rest = [w for w in words if w not in keys]
            for i in xrange(len(rest)):
                rest[i] = '-'+rest[i]
            if len(keys)==0: continue
            print (u' '.join(keys)).encode('utf-8') + ' '+ (u' '.join(rest)).encode('utf-8')

        words.insert(0,words.pop())

makeCombinations()
