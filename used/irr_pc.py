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
# TODO!
# parseAds and reTitle - must be called in threads
# http://kaliningrad.irr.ru/advert/116409169/

base_ads_url = 'http://kaliningrad.irr.ru'

class IrrAutoTarget:


    def makeDate(self):
        t = str(date.today())
        return t.split('-')

    def toDict(self):
        txt = re.sub(date_pat, "", self.text)
        if "document.write" in self.phone:
            self.phone = ""
        di = {'price':self.price,'subj':self.subject, 'text':txt, 'phone':self.phone, 'dep':'pc','src':'irr',
                'date':self.makeDate(), 'week':True}
        params = {}
        for name_value in self.fields:
            name = name_value[0]
            value = u''
            if len(name_value) > 1:
                value = u' '.join(name_value[1:])
            params.update({name:value})
        di.update({'params':params})
        di.update({'category':self.category})
        return di

    def match(self, look_for, where_to_look):
        for k in look_for:
            if k not in where_to_look: return False
            if look_for[k] != where_to_look[k]: return False
        return True

    def end_of_tag(self, tag_match, params):
        return tag_match and 'end' in params

    def walk(self):
        while True:
            params = yield
            if self.match({'tag':'h1'}, params):
                while True:
                    params = yield
                    ma = self.match({'tag':'h1'}, params)
                    if self.end_of_tag(ma, params): break
                    if 'data' in params:
                        self.subject+= params['data']

            if self.match({'tag':'b','id':'priceSelected'}, params):
                while True:
                    params = yield
                    ma = self.match({'tag':'b'}, params)
                    if self.end_of_tag(ma, params): break
                    if 'data' in params:
                        self.price+= params['data']

            if self.match({'tag':'span','class':'advert_text'}, params):
                while True:
                    params = yield
                    ma = self.match({'tag':'span'}, params)
                    if self.end_of_tag(ma, params): break
                    if 'data' in params:
                        self.text+= params['data']
                        
            # mainParams
            safe_count = 0
            if self.match({'tag':'table','id':'mainParams'}, params):
                while True:
                    safe_count +=1
                    params = yield
                    if 'data' in params:
                        self.kaliningrad = self.kaliningrad or u'калининград' in params['data'].lower()
                    if self.kaliningrad:
                        break
                    if safe_count>=100:
                        print "fuuuuuuuuuuuuuuuuuuuuuuck!"
                        break
            if self.match({'tag':'table','id':'allParams'}, params):
                got_fields = False
                while not got_fields:
                    params = yield
                    ma = self.match({'tag':'tr'}, params)
                    if self.end_of_tag(ma, params): continue
                    if ma:
                        got_header = False
                        while not got_header:
                            params = yield
                            ma = self.match({'tag':'th'}, params)
                            if self.end_of_tag(ma, params): break
                            if ma:
                                header = ""
                                while not got_header:
                                    params = yield
                                    if 'data' in params:
                                        header += params['data']
                                    else:
                                        got_header = True
                                self.fields.append([header.replace("\t","").replace("\n","")])

                        got_value = False
                        while not got_value:
                            params = yield
                            ma = self.match({'tag':'td'}, params)
                            if self.end_of_tag(ma, params): break
                            if ma:
                                value = ""
                                while not got_value:
                                    params = yield
                                    if 'data' in params:
                                        value += params['data']
                                    else:
                                        got_value = True
                                self.fields[-1].append(value.replace("\t","").replace("\n",""))

                    else:
                        if self.end_of_tag(self.match({'tag':'table'},params), params):
                            got_fields = True

            if self.match({'tag':'div','class':'wrapIcons'}, params) and len(re.findall(number_pat, ' ' + self.phone +  ' ')) == 0:
                while True:
                    params = yield
                    ma = self.match({'tag':'div'}, params)
                    if self.end_of_tag(ma, params):
                        break
                    if 'data' in params:
                        self.phone+= params['data']

    def __init__(self, category):
        self.kaliningrad = False
        self.price = ''
        self.text = ''
        self.phone = ''
        self.subject = ''
        self.price_pat = re.compile(u"[0-9]+[\.рубusd]?$")
        self.fields = []
        self.walker = self.walk()
        self.walker.next()
        self.category = category


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


def parseAds(f, external_id, category, remaining=None, parser=None, target=None):
    spoon = 1024*10
    if remaining is None:
        remaining = f.tell()
        # TODO! how do i know, that the received fileis more than 1024???
        target = IrrAutoTarget(category)
        parser=etree.HTMLParser(target=target)
        f.seek(0)
        rd = f.read(spoon)
        parser.feed(rd)
        remaining -= spoon
        d = deferLater(reactor, randint(1,3), parseAds, f, external_id, category, remaining, parser, target)
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
            if target.kaliningrad:
                d =couch.saveDoc(json)
            else:
                print "this is not kaliningrad"
                return None
            def ret(doc):
                answer = 'no phone for this ad: ' + base_ads_url + '/' + external_id \
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
            d = deferLater(reactor, randint(1,3), parseAds, f, external_id, category, remaining, parser, target)
            return d



title_re = re.compile('<a href="(/advert/[0-9]+/)"')

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

base_url ='http://kaliningrad.irr.ru/computers-devices/desktops/sort/date_create:desc/'

cats = {
    'pc':('/computers-devices/desktops/search/tab=users/sort/date_create:desc/',15),
    'notes':('/computers-devices/notebooks/search/tab=users/sort/date_create:desc/',20),
    'parts':('/computers-devices/hardware/search/tab=users/sort/date_create:desc/',25),
    'displ':('/computers-devices/monitors/search/tab=users/sort/date_create:desc/',5),
    'tablets':('/computers-devices/tablet/',3)
    }


def walkForAd(links, cat):
    defs = []
    i = 0
    for l in links:
        d = Deferred()
        d.addCallback(parseAds, l, cat)
        d.addErrback(grab.sendError)
        reactor.callLater(i,grab.downLoadPage, base_ads_url + l, reactor, d)
        i+=1
        defs.append(d)
    dl = DeferredList(defs)
    return dl


def send_error(failure):
    return send_email('admin@buildpc.ru', u'Ошибка в irr_pc.py', unicode(failure), sender=u'Калининградские объявления <inbox@buildpc.ru>')

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
    for cat,url_count in cats.items():

        for i in xrange(1,url_count[1]+1):
            d = Deferred()
            d.addCallback(reTitles)
            d.addErrback(send_error)
            d.addCallback(filterForNew)
            d.addErrback(send_error)
            d.addCallback(walkForAd, cat)
            d.addErrback(send_error)
            defs.append(d)
            _call = _grab(base_ads_url+url_count[0]+'page' + str(i) + '/', d)
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
        return send_email('admin@buildpc.ru', u'irr-auto crawl results', ''.join(pages) + "<div>thats the length of result list: " + str(len(li)) +  "</div>", sender=u'Компьютерный магазин Билд <inbox@buildpc.ru>')

    dl.addCallback(report)
    initial = _calls.pop(0)
    j = 0
    for c in _calls:
        defs[j].addCallback(c)
        j+=1
    initial('iniiiiiiiiiiiiiiiiiiiiiiit')
    # initial = deferLater(reactor, 0, _calls[0], 'initial call')
    # for c in _calls[1:]:
    #     initial.addCallback(c)
    return dl


# def _deleteMoscow(res):
#     for r in res['rows']:
#         if 'doc' in r and r['doc'] is not None:
#             couch.deleteDoc(r['doc']['_id'], r['doc']['_rev'])

# def deleteMoscow():
#     d = couch.listDoc(keys=to_delete, include_docs=True)
#     d.addCallback(_deleteMoscow)
#     return d
