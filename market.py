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
                divs = root.xpath('//div[@class="b-grade comment left'+str(i)+'"]')
                for d in divs:
                    td = d.xpath('//td[@class="b-grade__feedback grade-opinion-actions"]')
                    for t in td:
                        t.getparent().remove(t)
                    imgs = d.xpath('//img[@class="b-rating__icon"]')
                    for i in imgs:
                        i.getparent().remove(i)

                all_divs+=divs
            return all_divs
        else:
            rd = f.read(spoon)
            parser.feed(rd)
            remaining -= spoon
            d = deferLater(reactor, 0, parseMarket, f, remaining, parser)
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
