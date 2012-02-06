# -*- coding: utf-8  -*-
from twisted.internet import reactor#, threads
from lxml import etree
import re
from pc.used import grab
from pc.used.couch import couch, designID
from twisted.internet.defer import Deferred, DeferredList
import simplejson
from datetime import date
from pc.mail import send_email
from random import randint
from twisted.internet.task import deferLater

base_ads_url = 'http://www.newkaliningrad.ru/bulletin/'

class NewPCTarget(object):

    def makeDate(self):
        t = str(date.today())
        return t.split('-')

    def toDict(self):
        txt = re.sub(date_pat, "", self.text)
        if "document.write" in self.phone:
            self.phone = ""
        di = {'price':self.price,'subj':self.subject, 'text':txt, 'phone':self.phone, 'dep':'pc','src':'new',
                'date':self.makeDate(), 'week':True, 'email':self.email}
        params = {}
        for name_value in self.fields:
            name = name_value[0]
            value = u''
            if len(name_value) > 1:
                value = u' '.join(name_value[1:])
            params.update({name:value})
        di.update({'params':params})
        return di


    def walk(self):
        catch_text = False
        while True:
            params = yield
            if params.get('tag', '') =='h3' and params.get('class', '') =='detailtitle':
                while True:
                    params = yield
                    #just collect all data
                    if 'data' in params:
                        self.subject +=params['data']
                    if params.get('tag', '') =='h3' and params.get('end', False):
                        break
            if params.get('tag', '') =='h4' and params.get('class', '') =='detailprice':
                while True:
                    params = yield
                    if 'data' in params:
                        self.price+=params['data']
                    if params.get('tag', '') =='h4' and 'end' in params:
                        catch_text = True
                        break

            if catch_text and params.get('tag','')=='p':
                while True:
                    params = yield
                    if params.get('tag','')=='p' and 'end' in params:
                        catch_text = False
                        break
                    if 'data' in params:
                        self.text+=params['data']
                
            if params.get('tag','') == 'table' and params.get('class','')=='form_table':
                while True:
                    params = yield
                    proceed_link = False
                    if params.get('tag') == 'p':
                        while True:
                            params = yield
                            if params.get('tag','') == 'a' and 'end' not in params:
                                proceed_link = True
                            if params.get('tag','') == 'a' and 'end' in params:
                                proceed_link = True
                            if params.get('data', False) and not proceed_link:
                                if '@' in params['data']:
                                    self.email += params['data']
                                else:
                                    self.phone += params['data']
                            if params.get('tag','') == 'p' and 'end' in params:
                                break
                    if params.get('tag','')=='table' and 'end' in params:
                        break


    def __init__(self):
        self.price = ''
        self.text = ''
        self.phone = ''
        self.email = ''
        self.subject = ''
        self.price_pat = re.compile(unicode("[0-9 ]+[рубusd\.\$]+", 'utf-8'), re.UNICODE)

        self.fields = []
        self.walker = self.walk()
        self.walker.next()


    def start(self, tag, attrib):
        params = {'tag':tag}
        for k,v in attrib.items():
            params.update({k:v})
        self.walker.send(params)


    def end(self, tag):
        params = {'tag':tag, 'end':'end'}
        self.walker.send(params)


    def data(self, data):
        self.walker.send({'data':data})

    def comment(self, text):
        pass

    def close(self):
        return self




def read1k(f):
    return f.read(1024)



number_pat = re.compile("[ ]+[0-9\-\+ ]+[ ]+")
price_pat = re.compile(unicode("[ ]+[0-9 ]+[руб]+", 'utf-8'), re.UNICODE)
date_pat = re.compile(unicode("Дата выхода объявления в печатном издании:.*$", 'utf-8'), re.UNICODE)


def findPhone(text):
    text = text.replace(u'т.', ' ').replace('.',' ')
    groups = re.findall(number_pat, text + ' ')
    clean = [number.replace("+","").replace("-","").replace(" ","") for number in groups]
    # 6 digits minimum
    clean = [c for c in clean if len(c) >= 6]
    if len(clean) == 1:
        return clean[0]

    # price are always consist of zeros
    clean = [c for c in clean if "000" not in c]
    if len(clean) == 1:
        return clean[0]
    # 89114691892
    clean = [c for c in clean if c.startswith("89")]
    if len(clean) == 1:
        return clean[0]
    #79114691892
    clean = [c for c in clean if c.startswith("79")]
    if len(clean) == 1:
        return clean[0]
    return None


def findPrice(t, price):
    if re.match(number_pat, " " + price) is not None:
        return price
    groups = re.findall(price_pat, t)
    if len(groups) == 1:
        return groups[0]
    else:
        return price


def parseAds(f, external_id, remaining=None, parser=None, target=None):
    spoon = 1024*10
    if remaining is None:
        remaining = f.tell()
        # TODO! how do i know, that the received fileis more than 1024???
        target = NewPCTarget()
        parser=etree.HTMLParser(target=target, encoding='cp1251')
        f.seek(0)
        rd = f.read(spoon)
        parser.feed(rd)
        remaining -= spoon
        d = deferLater(reactor, 0, parseAds, f, external_id, remaining, parser, target)#randint(1,3)
        return d
    else:
        if remaining < spoon:
            rd = f.read(remaining)
            parser.feed(rd)
            f.close()
            try:
                parser.close()
            except:
                pass

            di = target.toDict()
            di.update({'external_id':external_id})

            num = re.sub(r'\D', "", di["phone"])
            if len(num) == 0:
                possible_phone = findPhone(di['text'])
                if possible_phone is not None:
                    di['phone'] = possible_phone
                    num = possible_phone
            di['price'] = findPrice(di['text'], di['price'])
            json = simplejson.dumps(di)
            d =couch.saveDoc(json)
            def ret(doc):
                answer = 'no phone for this ad: ' + base_ads_url + external_id \
                    + ' stored at ' +doc['id']
                if len(num)>0:
                    answer = "storing " + base_ads_url + '/' + external_id + \
                        " at:" + ' stored at '+ doc['id']
                return answer
            d.addCallback(ret)
            return d
        else:
            rd = f.read(spoon)
            parser.feed(rd)
            remaining -= spoon
            d = deferLater(reactor, 0, parseAds, f, external_id, remaining, parser, target)#randint(1,3)
            return d



title_re = re.compile('<a href="/bulletin/(see_one/[0-9]+)"')

def reTitles(f):
    f.seek(0)
    src = f.read()
    f.close()
    links = re.findall(title_re, src)
    return [l for l in set(links)]



def filterLinks(rows,links):
    old = set([r['key'] for r in rows['rows']])
    filtered = [l for l in links if l not in old]
    return filtered

def filterForNew(links):
    d = couch.openView(designID, "external_ids", keys=links, stale=False)
    d.addCallback(filterLinks, links)
    return d

def shutDown(ignored):
    reactor.stop()

base_url = 'http://www.newkaliningrad.ru/bulletin/category/itech/page/'

def walkForAd(links):
    defs = []
    i = 0
    for l in links:
        d = Deferred()
        d.addCallback(parseAds, l)
        d.addErrback(grab.sendError)
        reactor.callLater(i*10,grab.downLoadPage, base_ads_url + l, reactor, d)
        i+=1
        defs.append(d)
    dl = DeferredList(defs)
    return dl


def send_error(failure):
    return send_email('admin@buildpc.ru', u'Ошибка в new_pc.py', unicode(failure), sender=u'Калининградские объявления <inbox@buildpc.ru>')

def _grab(url, d):
    def __grab(some):
        grab.downLoadPage(url, reactor, d)
        return some
    return __grab

def crawl():
    defs = []
    # defs = [Deferred() for x in ]
    # TODO! errors to email
    _calls = []

    for i in xrange(15):#24
        d = Deferred()
        d.addCallback(reTitles)
        d.addErrback(send_error)
        d.addCallback(filterForNew)
        d.addErrback(send_error)
        d.addCallback(walkForAd)
        d.addErrback(send_error)
        defs.append(d)
        _call = _grab(base_url+str(i+1) + '/', d)
        _calls.append(_call)
    dl = DeferredList(defs)
    def report(li):
        i = 0
        pages = []
        for tu in li:
            if tu[0]:
                page= []
                for res in tu[1]:
                    if res[0]:
                        ap = 'none'
                        if type(res[1]) is str or type(res[1]) is unicode:
                            ap = res[1]
                        else:
                            ap = ' '.join([str(r) for r in res[1]])
                        page.append('<div>' + ap + '</div>')
                    else:
                        page.append('<div>fail link at page: ' + str(i) + '</div>')
                pages.append('<p>' + ''.join(page) + '</p>')
            else:
                pages.append('<p>fail whole page: ' + i + '</p>')
            i+=1
        return send_email('admin@buildpc.ru', u'new-auto crawl results', ''.join(pages) + "<div>thats the length of result list: " + str(len(li)) +  "</div>", sender=u'Компьютерный магазин Билд <inbox@buildpc.ru>')

    dl.addCallback(report)
    initial = _calls.pop(0)
    j = 0

    def callater(func):
        def cl(some):
            reactor.callLater(100,func, some)
        return cl


    for c in _calls:
        defs[j].addCallback(callater(c))
        j+=1
    initial('iniiiiiiiiiiiiiiiiiiiiiiit')
    # initial = deferLater(reactor, 0, _calls[0], 'initial call')
    # for c in _calls[1:]:
    #     initial.addCallback(c)
    return dl
