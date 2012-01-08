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


# class Marketarget(object):
#     def __init__(self):
#         self.walker = self.walk()
#         self.walker.next()
#         self.readyHtml = ''

#     def start(self, tag, attrib):
#         params = {'tag':tag, 'start':'start'}
#         for k,v in attrib.items():
#             params.update({k:v})
#         self.walker.send(params)


#     def end(self, tag):
#         params = {'tag':tag, 'end':'end'}
#         self.walker.send(params)

#     def data(self, data):
#         self.walker.send({'data':data})

#     def comment(self, text):
#         pass

#     def close(self):
#         return self


#     def walk(self):
#         while True:
#             params = yield
#             comp = Comparator(params)


empty_review_pat = re.compile("Комментариев пока нет")
empty_comment_pat = re.compile("Вы можете стать первым.")

def parseMarket(f, remaining=None, parser=None):
    spoon = 1024*10
    if remaining is None:
        remaining = f.tell()
        parser=etree.HTMLParser(encoding='utf-8')
        f.seek(0)
        rd = f.read(spoon)
        parser.feed(rd)
        remaining -= spoon
        d = deferLater(reactor, 0, parseMarket, f, remaining, parser)
        return d
    else:
        if remaining < spoon:
            rd = f.read(remaining)
            parser.feed(rd)
            f.close()
            root = parser.close()
            all_divs = []
            for i in xrange(3):
                all_divs+=root.xpath('//div[@class="b-grade comment left'+str(i)+'"]')
            return all_divs
        else:
            rd = f.read(spoon)
            parser.feed(rd)
            remaining -= spoon
            d = deferLater(reactor, 1, parseMarket, f, remaining, parser)
            return d
     

def getMarket(card):
    agent = Agent(reactor)
    headers = {}
    for k,v in standard_headers.items():
        if k == 'User-Agent':
            headers.update({'User-Agent':[standard_user_agents[randint(0,len(standard_user_agents)-1)]]})
        else:
            headers.update({k:v})
    
    c = defer.Deferred()
    c.addCallback(parseMarket)
    r = defer.Deferred()
    r.addCallback(parseMarket)


    request_comments = agent.request('GET', str(card.marketComments),Headers(),None)
    request_comments.addCallback(downloadPage, c)
    request_reviews = agent.request('GET', str(card.marketReviews),Headers(),None)
    request_reviews.addCallback(downloadPage, r)
    return defer.DeferredList((c,r))
