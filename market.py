# -*- coding: utf-8 -*-
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from pc.catalog import standard_headers, standard_user_agents, downloadPage, NewTarget, Comparator
from random import randint
from twisted.internet import defer
import re
from urllib import quote_plus
from lxml import etree
from twisted.internet.task import deferLater






def parseMarket(f, url='url', remaining=None, parser=None):
    spoon = 1024*10
    if remaining is None:
        remaining = f.tell()
        parser=etree.HTMLParser(encoding='utf-8')
        f.seek(0)
        rd = f.read(spoon)
        parser.feed(rd)
        remaining -= spoon
        d = deferLater(reactor, 0, parseMarket, f, url, remaining, parser)
        return d
    else:
        if remaining < spoon:
            rd = f.read(remaining)
            parser.feed(rd)
            f.close()
            root = parser.close()
            all_divs = []
            for i in xrange(3):
                klass = 'comment left'+str(i)
                if not 'forums' in url:
                    klass = "b-grade " + klass
                divs = root.xpath('//div[@class="'+klass+'"]')
                for d in divs:
                    td = d.xpath('//td[@class="b-grade__feedback grade-opinion-actions"]')
                    for t in td:
                        t.getparent().remove(t)
                    imgs = d.xpath('//img[@class="b-rating__icon"]')
                    for i in imgs:
                        i.getparent().remove(i)

                all_divs+=divs
            globals()['gMarket_Cached'][url] = all_divs
            return all_divs
        else:
            rd = f.read(spoon)
            parser.feed(rd)
            remaining -= spoon
            d = deferLater(reactor, 0, parseMarket, f, url, remaining, parser)
            return d



gMarket_Cached = {}

def getMarket(card):
    cached = globals()['gMarket_Cached']
    if card.marketComments in cached and card.marketReviews in cached:
        d1 = defer.Deferred()
        d1.addCallback(lambda x: cached[card.marketComments])
        d1.callback(None)
        d2 = defer.Deferred()
        d2.addCallback(lambda x: cached[card.marketReviews])
        d2.callback(None)
        return defer.DeferredList((d1,d2))

    agent = Agent(reactor)
    headers = {}
    for k,v in standard_headers.items():
        if k == 'User-Agent':
            headers.update({'User-Agent':[standard_user_agents[randint(0,len(standard_user_agents)-1)]]})
        else:
            headers.update({k:v})

    c = defer.Deferred()
    c.addCallback(parseMarket, url=card.marketComments)
    r = defer.Deferred()
    r.addCallback(parseMarket, url=card.marketReviews)


    request_comments = agent.request('GET', str(card.marketComments),Headers(),None)
    request_comments.addCallback(downloadPage, c)
    request_reviews = agent.request('GET', str(card.marketReviews),Headers(),None)
    request_reviews.addCallback(downloadPage, r)
    return defer.DeferredList((c,r))
