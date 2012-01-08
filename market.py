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
empty_pat = re.compile("пока нет")
def parseMarket(f):
    f.seek(0)
    content = f.read()
    f.close()
    return re.search(empty_pat, content) is not None
    

def getMarket(url):
    agent = Agent(reactor)
    headers = {}
    for k,v in standard_headers.items():
        if k == 'User-Agent':
            headers.update({'User-Agent':[standard_user_agents[randint(0,len(standard_user_agents)-1)]]})
        else:
            headers.update({k:v})
    d = defer.Deferred()
    d.addCallback(parseMarket)
    # print str(url)
    request_d = agent.request('GET', str(url),Headers(),None)
    request_d.addCallback(downloadPage, d)
    return d
