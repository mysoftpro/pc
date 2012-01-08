# -*- coding: utf-8 -*-
from twisted.web.client import Agent
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from pc.catalog import standard_headers, standard_user_agents, downloadPage
from random import randint
from twisted.internet import defer
import re
from urllib import quote_plus

# empty_pat = re.compile(unicode("пока нет", 'utf-8'), re.UNICODE)
empty_review_pat = re.compile("Комментариев пока нет")
empty_comment_pat = re.compile("Вы можете стать первым.")

def parseComments(f):
    f.seek(0)
    content = f.read()
    f.close()
    return re.search(empty_comment_pat, content) is None


def parseReviews(f, url):
    f.seek(0)
    content = f.read()
    f.close()
    return re.search(empty_review_pat, content) is None
     

def getMarket(card):
    agent = Agent(reactor)
    headers = {}
    for k,v in standard_headers.items():
        if k == 'User-Agent':
            headers.update({'User-Agent':[standard_user_agents[randint(0,len(standard_user_agents)-1)]]})
        else:
            headers.update({k:v})
    c = defer.Deferred()
    c.addCallback(parseComments)
    r = defer.Deferred()
    r.addCallback(parseReviews, card.marketReviews)


    request_comments = agent.request('GET', str(card.marketComments),Headers(),None)
    request_comments.addCallback(downloadPage, c)
    request_reviews = agent.request('GET', str(card.marketReviews),Headers(),None)
    request_reviews.addCallback(downloadPage, r)
    return defer.DeferredList((c,r))
