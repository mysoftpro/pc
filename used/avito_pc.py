# -*- coding: utf-8  -*-
from twisted.internet import reactor, threads
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
from pc.catalog import standard_headers,standard_user_agents
from twisted.web.http_headers import Headers
from twisted.web.client import Agent
from twisted.internet import defer
from twisted.internet.protocol import Protocol
from cStringIO import StringIO

base_ads_url = 'http://www.avito.ru/items/'

class AvitoPCTarget(object):

    def makeDate(self):
        t = str(date.today())
        return t.split('-')

    def toDict(self):
        txt = re.sub(date_pat, "", self.text)
        if "document.write" in self.phone:
            self.phone = ""
        di = {'price':self.price,'subj':self.subject, 'text':txt, 'phone':self.phone, 'dep':'pc','src':'avito',
                'date':self.makeDate(), 'week':True, 'email':self.email, 'category':self.category}
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
        while True:
            params = yield
            if params.get('tag', '') =='h1':
                while True:
                    params = yield
                    #just collect all data
                    if 'data' in params:
                        self.subject +=params['data']
                    if params.get('tag', '') =='h1' and 'end' in params:
                        break
            if params.get('tag', '') =='dd' and params.get('id', '') =='desc_text':
                while True:
                    params = yield
                    if 'data' in params:
                        self.text+=params['data']
                    if params.get('tag', '') =='dd' and 'end' in params:
                        break
            if params.get('tag','') == 'span' and params.get('class','') =='p_i_price'\
                    and 'content' in params:
                self.price = params['content']

            if params.get('tag','')=='input' and params.get('id','')=='phone_key' and\
                    'value' in params:
                self.phone = params['value']

    def __init__(self, category):
        self.price = ''
        self.text = ''
        self.phone = ''
        self.email = ''
        self.subject = ''
        self.price_pat = re.compile(unicode("[0-9 ]+[рубusd\.\$]+", 'utf-8'), re.UNICODE)

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




class ImageReceiver(Protocol):
    def __init__(self, finish):
        self.file = StringIO()
        self.finish = finish

    def dataReceived(self, bytes):
        self.file.write(bytes)

    def connectionLost(self, reason):
        self.file.seek(0)
        self.finish.callback(self.file)



from PIL import Image

avito_letters = {
    35046:'1',
    90219:'2',
    89445:'3',
    74991:'4',
    87729:'5',
    89934:'6',
    80247:'7',
    85905:'8',
    89616:'9',
    88635:'0'}

def parseAvitoImage(imageContent, ob):#
    # f = open('/home/aganzha/Desktop/avito_phone_4.png')
    # src = f.read()
    # f.close()
    im = Image.open(imageContent)#StringIO(src)
    bim = im#.convert('1')
    # bim.save('/home/aganzha/Desktop/a.png')
    pixels = bim.load()
    width = bim.size[0]
    height = bim.size[1]

    letters = []

    def untill_black(start_x, calls):
        if start_x == width-1:return
        if calls >=100:
            return
        found = 0
        # catch 2 black pixels!
        for x in xrange(start_x, width):
            for y in xrange(height):
                point = reduce(lambda x,y:x+y,pixels[x,y])
                found += int(point != 765)
                if found >= 2:
                    break
            if found >= 2:
                break
            else:
                found = 0
        untill_white(x, calls+1)

    def untill_white(start_x, calls):
        if start_x == width-1:return
        if calls >=100:
            return
        letter = 0
        for x in xrange(start_x,width):
            all_white = True
            column = 0
            for y in xrange(0,height):
                point = reduce(lambda x,y:x+y,pixels[x,y])
                all_white = all_white and point == 765
                column+=point
            all_white = all_white or column >= 14535 # if has only 1 pixel - let it be white
            if all_white:
                break
            letter+=column
        letters.append(letter)
        untill_black(x, calls+1)
    untill_black(0,0)
    real_phone = ''
    for l in letters:
        if not l in avito_letters:
            real_phone = ''
            break
        real_phone += avito_letters[l]
    ob['phone'] = real_phone
    imageContent.close()
    return ob

def saveWithPhone(ob):
    d =couch.saveDoc(ob)
    def ret(doc):
        print "saved!"
        print doc['id']
        answer = 'no phone for this ad: ' + base_ads_url + ob['external_id'] \
            + ' stored at ' +doc['id']
        if ob['phone']!='':
            answer = "storing " + base_ads_url + '/' + ob['external_id'] + \
                " at:" + ' stored at '+ doc['id']
        return answer
    d.addCallback(ret)
    return d


def getAvitoImage(ob):
    image_url = 'http://www.avito.ru/items/phone/'+ob['external_id']+'?pkey='+ob['phone']
    agent = Agent(reactor)
    headers = {}

    for k,v in standard_headers.items():
        if k == 'User-Agent':
            headers.update({'User-Agent':[standard_user_agents[randint(0,len(standard_user_agents)-1)]]})
        else:
            headers.update({k:v})

    d = defer.Deferred()
    image_request = agent.request('GET', str(image_url),Headers(headers),None)
    image_request.addCallback(lambda response: response.deliverBody(ImageReceiver(d)))

    def toThread(sio):
        d = threads.deferToThread(parseAvitoImage, sio, ob)
        d.addCallback(saveWithPhone)
        return d
    d.addCallback(toThread)
    # d.addCallback(parseAvitoImage, ob)
    return d



def parseAds(f, external_id, cat, remaining=None, parser=None, target=None):
    spoon = 1024*10
    if remaining is None:
        remaining = f.tell()
        # TODO! how do i know, that the received fileis more than 1024???
        target = AvitoPCTarget(cat)
        parser=etree.HTMLParser(target=target)
        f.seek(0)
        rd = f.read(spoon)
        parser.feed(rd)
        remaining -= spoon
        d = deferLater(reactor, 0, parseAds, f, external_id, cat, remaining, parser, target)#randint(1,3)
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
            return getAvitoImage(di)

        else:
            rd = f.read(spoon)
            parser.feed(rd)
            remaining -= spoon
            d = deferLater(reactor, 0, parseAds, f, external_id, cat, remaining, parser, target)#randint(1,3)
            return d



title_re = re.compile('href="/items/(kaliningrad[^0-9]+[0-9]+)"')

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

def walkForAd(links, cat):
    defs = []
    i = 0
    for l in links:
        print "---------------------!"
        print l
        d = Deferred()
        d.addCallback(parseAds, l, cat)
        d.addErrback(grab.sendError)
        reactor.callLater(i*10,grab.downLoadPage, base_ads_url + l, reactor, d)
        i+=1
        defs.append(d)
    dl = DeferredList(defs)
    return dl


def send_error(failure):
    return send_email('admin@buildpc.ru', u'Ошибка в avito_pc.py', unicode(failure), sender=u'Калининградские объявления <inbox@buildpc.ru>')

def _grab(url, d):
    def __grab(some):
        grab.downLoadPage(url, reactor, d)
        return some
    return __grab




base_url = 'http://www.avito.ru/catalog/'
cats = {'pc':('nastolnye_kompyutery-31/kaliningradskaya_oblast-629990',1),
        'notes':('noutbuki-98/kaliningradskaya_oblast-629990',3),
        'parts':('komplektuyuschie_i_monitory-100/kaliningradskaya_oblast-629990', 3),
        'tablets':('planshety_i_aelektronnye_knigi-96/kaliningradskaya_oblast-629990',2)
    }


def crawl():
    defs = []
    # defs = [Deferred() for x in ]
    # TODO! errors to email
    _calls = []
    for cat,tu in cats.items():
        url = tu[0]
        for i in xrange(tu[1]):#24
            postfix = '/page'+str(i+1)
            if i==0:
                postfix = ''
            d = Deferred()
            d.addCallback(reTitles)
            d.addErrback(send_error)
            d.addCallback(filterForNew)
            d.addErrback(send_error)
            d.addCallback(walkForAd, cat)
            d.addErrback(send_error)
            defs.append(d)
            _call = _grab(base_url+url + postfix, d)
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
        return send_email('admin@buildpc.ru', u'avito-auto crawl results', ''.join(pages) + "<div>thats the length of result list: " + str(len(li)) +  "</div>", sender=u'Компьютерный магазин Билд <inbox@buildpc.ru>')

    dl.addCallback(report)
    initial = _calls.pop(0)
    j = 0
    # here i will request one by one from the calls list
    # but not immidiately. after some seconds
    def callater(func):
        def cl(some):
            reactor.callLater(100,func, some)
        return cl

    for c in _calls:
        defs[j].addCallback(callater(c))
        j+=1
    initial('iniiiiiiiiiiiiiiiiiiiiiiit')
    return dl
