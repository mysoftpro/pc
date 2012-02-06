# -*- coding: cp1251 -*-
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
import gzip
#import tempfile
#from lxml import etree
#import sys
from cStringIO import StringIO
from pc.mail import send_email
from random import randint


def sendError(failure):
    return send_email('admin@buildpc.ru',
                      u'ошибка в grab.py',
                      unicode(failure), sender=u'Компьютерный магазин Билд <inbox@buildpc.ru>')

class Receiver(Protocol):
    def __init__(self, finished, encoding):
        self.finished = finished
        self.file = StringIO()
        self.gzip = False
        if "gzip" == encoding:
            self.gzip = True


    def dataReceived(self, bytes):
        self.file.write(bytes)


    def ungzip(self):
        self.file.seek(0)
        gzipper = gzip.GzipFile(fileobj=self.file)
        self.file = StringIO(gzipper.read())
        return self.file

    def connectionLost(self, reason):
        # print self.file.tell()
        # so. the file is at the end, and it tell() me how much bytes it has!
        if self.gzip:
            self.ungzip()
        self.file.seek(0,2)
        self.finished.callback(self.file)

standard_user_agents = ['Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.57 Safari/534.24',
                        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15',
                        'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.60 Safari/534.24',
                        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.3; Creative AutoUpdate v1.40.02)',
                        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; GTB6.4; .NET CLR 1.1.4322; FDM; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)',
                        'Opera/9.80 (Windows Mobile; WCE; Opera Mobi/WMD-50433; U; en) Presto/2.4.13 Version/10.00'
                        ]
standard_headers = {'User-Agent': ['Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'],
                    'Accept': ['text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'],
                    'Accept-Charset': ['ISO-8859-1,utf-8;q=0.7,*;q=0.7'],
                    'Accept-Encoding': ['gzip,deflate'],
                    'Accept-Language': ['en-us,en;q=0.5'],
                    'Keep-Alive': ['115'],
                    'Connection': ['keep-alive']}


def getDomain(url):
    res = url.split('//')[1].split('/')[0]
    return res

def compareDomain(d1,d2):
    if d1 == d2:
        return True
    s1 = d1.split('.')
    s1.reverse()
    s2 = d2.split('.')
    s2.reverse()
    if (s1[0] == s2[0]) and (s1[1] == s2[1]):
        return True
    return False


def cbRequest(response, url_to, tries, futher_d, agent):
    glob_tries = tries
    if (response.code == 302 or response.code == 301) and glob_tries<10:
        cookies= []
        url = ''
        enc = None
        for h in response.headers.getAllRawHeaders():
            if h[0] == 'Set-Cookie':
                cookies = h[1]
            if h[0] == 'Location':
                url = h[1][0]
        clean_cookies = []

        new_headers = standard_headers
        if compareDomain(getDomain(url_to),getDomain(url)):
            for c in cookies:
                clean_c = c.split(';')[0]
                # agn???
                if (not 'auth_error' in c) and (clean_c not in clean_cookies):
                    clean_cookies.append(clean_c)
            if (len(clean_cookies) > 0):
                new_headers.update({'Cookie':[';'.join(clean_cookies)]})
        else:
            if 'Cookie' in new_headers:
                new_headers.pop('Cookie')
        new_headers.update({'Host':[getDomain(url)]})
        rd = agent.request('GET',url,Headers(new_headers),None)
        rd.addCallback(cbRequest, url, glob_tries+1, futher_d, agent)
        rd.addErrback(sendError)
        return rd
    else:
        enc = None
        cookies = None
        for h in response.headers.getAllRawHeaders():
            if h[0] == 'Content-Encoding':
                enc = h[1][0]
            #if h[0] == 'Set-Cookie':
            #    cookies = [c.split(';')[0]  for c in h[1]]
        response.deliverBody(Receiver(futher_d, enc))
        return futher_d

def downLoadPage(url, reactor, futher_d):
    print "go for this url: " + url
    agent = Agent(reactor)
    headers = {}
    for k,v in standard_headers.items():
        if k == 'User-Agent':
            headers.update({'User-Agent':[standard_user_agents[randint(0,len(standard_user_agents)-1)]]})
        else:
            headers.update({k:v})                            
    request_d = agent.request('GET', url,Headers(headers),None)
    request_d.addCallback(cbRequest, url, 0, futher_d, agent)
    request_d.addErrback(sendError)
    return futher_d
