# -*- coding: utf-8 -*-
from pc.secure import xml_source,xml_method, xml_login, xml_password, xml_key,new_password,new_user
from lxml import etree
from twisted.python import log
import sys
import gzip
from twisted.web.xmlrpc import Proxy
import base64
from cStringIO import StringIO
from twisted.web.resource import Resource, ForbiddenResource
from pc.couch import couch, designID
import simplejson
from twisted.internet import reactor
from twisted.web.client import Agent
from random import randint
from twisted.web.http_headers import Headers
from twisted.internet.protocol import Protocol
from twisted.internet import defer
import os
from datetime import datetime
from pc.mail import send_email
from twisted.web.server import NOT_DONE_YET
from twisted.internet.defer import succeed
from twisted.web.iweb import IBodyProducer
from zope.interface import implements
from urllib import quote_plus
from twisted.internet.task import deferLater
import re

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


gLastUpdate = None

class XmlGetter(Resource):
    isLeaf = True
    allowedMethods = ('GET','POST')

    def pr(self, fail):
	log.startLogging(sys.stdout)
	log.msg(fail)
	send_email('admin@buildpc.ru',
		   u'Ошибка обновления каталога',
		   unicode(fail),
		   sender=u'Компьютерный магазин <inbox@buildpc.ru>')

    def storeWholeCatalog(self, res):
	src = base64.decodestring(res)
	sio = StringIO(src)
	gz = gzip.GzipFile(fileobj=sio)

	tree = etree.parse(gz)
	root = tree.getroot()
	jsroot = xmlToJson(toDict(root.attrib), root)
	d = couch.saveDoc(jsroot, docId="catalog")
	d.addErrback(self.pr)

    def storeItem(self, res, gen):
	try:
	    item = gen.next()
	except StopIteration:
	    return
	d = couch.saveDoc(item, docId=item.pop('code'))
	d.addCallback(self.storeItem, gen)
	d.addErrback(self.pr)

    def storeDocs(self, res):
	src = base64.decodestring(res)
	sio = StringIO(src)
	gz = gzip.GzipFile(fileobj=sio)
	tree = etree.parse(gz)
	root = tree.getroot()
	gen = xmlToDocs([], root)
	self.storeItem(None, gen)


    def compareItem(self, some, item, sio):
	raw_doc = sio.getvalue()
	sio.close()
	doc = simplejson.loads(raw_doc)
	component_changed = False
	for k,v in doc.items():
	    if k in item:
		if doc[k] != item[k]:
		    # TODO - treat changes here!
		    component_changed = True
		    doc[k] = item[k]
	if component_changed:
	    d = couch.addAttachments(doc, raw_doc, version=True)
	    # TODO! drop some later attachments!
	    # if updates are every hour - store just 8 of them, for example
	    d.addCallback(lambda _doc:couch.saveDoc(_doc))
	    d.addErrback(self.pr)
	    return d

    def cleanDocs(self, _all_docs, codes):
	all_count = 0
	deleted_count = 0
	for row in _all_docs['rows']:
	    try:
		int(row['id'])
	    except ValueError:
		continue
	    all_count +=1
	    if row['id'] not in codes:
		if 'mystock' in row['value'] and row['value']['mystock']>0:
		    pass
		else:
		    couch.deleteDoc(row['id'], row['value'])
		    deleted_count +=1
	# destroy cache here!
	from pc import root
	root.clear_cache()
	send_email('admin@buildpc.ru',
		   u'Обновление wit-tech',
		   u'Всего позиций:' + unicode(all_count) + u', удалено позиций:' + unicode(deleted_count),
		   sender=u'Компьютерный магазин <inbox@buildpc.ru>')

    def getItem(self, res, gen, codes):
	try:
	    item = gen.next()
	except StopIteration:
	    # separate view
	    _all = couch.openView(designID,'codes',stale=False) #couch.listDoc()
	    _all.addCallback(self.cleanDocs, codes)
	    _all.addErrback(self.pr)
	    return
	sio = StringIO()
	item_code = item.pop('code')
	codes.add(item_code)
	d = couch.openDoc(item_code, writer=sio)
	def co(res):
	    self.compareItem(res, item, sio)
	def st(fail):
	    c = couch.saveDoc(item, docId=item_code)
	    c.addErrback(self.pr)
	d.addCallbacks(co,st)
	d.addErrback(self.pr)
	d.addCallback(self.getItem, gen, codes)
	d.addErrback(self.pr)
	return d


    def compareDocs(self, res):
	src = base64.decodestring(res)
	sio = StringIO(src)
	gz = gzip.GzipFile(fileobj=sio)

	# f = open(os.path.join(os.path.dirname(__file__), str(datetime.now()).replace(" ","_").replace(":","-")) + ".xml", 'w')
	# f.write(gz.read())
	# f.close()
	gz.seek(0)
	tree = etree.parse(gz)
	root = tree.getroot()
	gen = xmlToDocs([], root)
	self.getItem(None, gen, set())

    def render_GET(self, request):
	key = request.args.get('key', [None])[0]
	if key is None or key != xml_key:
	    return "fail"
	proxy = Proxy(xml_source)
	op = request.args.get('op', [None])[0]
	if op is not None:
	    if op == 'store':
		proxy.callRemote(xml_method, xml_login, xml_password).addCallbacks(self.storeDocs, self.pr)
	    elif op == 'compare' or op == 'update':
		proxy.callRemote(xml_method, xml_login, xml_password).addCallbacks(self.compareDocs, self.pr)
	    elif op == 'descr':
		print "try to store"
		self.storeDescription(request)
	return "ok"

    def render_OPTIONS(self, request):
	for i in request.headers:
	    print i
	    print request.headers[i]
	# print request.headers.getAllRawHeaders()
	request.responseHeaders = Headers({'Allow':['POST', 'GET'], 'Access-Control-Allow-Origin': ['*']})
	return "ok"

    def render_POST(self, request):
	op = request.args.get('op', [None])[0]
	if op == 'descr':
	    print "try to store"
	    self.storeDescription(request)


    def noSuchDoc(self, _id):
	def no(fail):
	    print fail
	    print _id
	return no

    def storeDescription(self, request):
	_id = request.args.get('code')[0]
	print "store! " + str(_id)
	_description = simplejson.loads(request.args.get('desription')[0][1:-1])
	d = couch.openDoc(_id)
	d.addErrback(self.noSuchDoc(_id))
	d.addCallback(self.saveDescription, _description)


    image_url = 'http://wit-tech.ru/img/get/file/'

    def saveDescription(self, doc, description):
	if doc is None: return
	print "save! " + doc["_id"]
	if 'description' in doc:
	    doc['description'] = description
	else:
	    doc.update({'description':description})
	if 'imgs' not in doc['description']:
	    couch.saveDoc(doc)
	else:
	    self.getImage(doc)

    def imgReceiverFactory(self, doc, img, d):
	def factory(response):
	    response.deliverBody(ImageReceiver(doc, img+'.jpg', d))
	return factory



    def getImage(self, doc):
	agent = Agent(reactor)
	headers = {}
	defs = []
	for img in doc['description']['imgs']:
	    for k,v in standard_headers.items():
		if k == 'User-Agent':
		    headers.update({'User-Agent':[standard_user_agents[randint(0,len(standard_user_agents)-1)]]})
		else:
		    headers.update({k:v})

	    url = self.image_url + img
	    d = defer.Deferred()
	    image_request = agent.request('GET', str(url),Headers(headers),None)
	    image_request.addCallback(self.imgReceiverFactory(doc, img, d))
	    image_request.addErrback(self.pr)
	    defs.append(d)
	li = defer.DeferredList(defs)
	li.addCallback(self.addImages, doc)
	li.addErrback(self.pr)
	return d

    def addImages(self, images, doc):
	attachments = {}
	for i in images:
	    if i[0]:
		attachments.update(i[1])
	print "adding image!!!!!!!!!!"
	d = couch.addAttachments(doc, attachments)
	d.addCallback(lambda _doc:couch.saveDoc(_doc))
	d.addErrback(self.pr)

class ImageReceiver(Protocol):
    def __init__(self, doc, name, finish):
	self.doc = doc
	self.name = name
	self.file = StringIO()
	self.finish = finish

    def dataReceived(self, bytes):
	self.file.write(bytes)


    def connectionLost(self, reason):
	self.file.seek(0,2)
	# d = couch.addAttachments(self.doc, {self.name:self.file.getvalue()})
	# d.addCallback(lambda x: self.finish.callback(x)
	self.finish.callback({self.name:self.file.getvalue()})
	self.file.close()




def toDict(attr):
    res = {}
    for k,v in attr.iteritems():
	v = v.replace('>', '')
	if v == '':
	    v = '0'
	try:
	    if k=='stock1' or k=='ordered' or k=='reserved' or k=='inCart':
		v = int(v)
	    if k=='price':
		v = float(v)
	except ValueError:
	    print "----------------------------------"
	    print k
	    print v.encode('utf-8')
	res.update({k:v})
    return res



def xmlToDocs(catalog_obs, catalog):
    for el in catalog:
	if el.tag == 'catalog':
	    new_catalog_obs = [c for c in catalog_obs]
	    new_catalog_obs.append(toDict(el.attrib))
	    gen = xmlToDocs(new_catalog_obs, el)
	    for item in gen:
		yield item
	elif el.tag == 'item':
	    item = toDict(el.attrib)
	    item.update({'catalogs':catalog_obs})
	    item.update({'text':el.text})
	    yield item


def xmlToJson(catalog_ob, catalog):
    catalog_ob.update({'xmltype':catalog.tag})
    for el in catalog:
	if el.tag == 'catalog':
	    if not 'catalogs' in catalog_ob:
		catalog_ob['catalogs'] = []
	    catalog_ob['catalogs'].append(xmlToJson(toDict(el.attrib), el))
	elif el.tag == 'item':
	    if not 'items' in catalog_ob:
		catalog_ob['items'] = []
	    item = toDict(el.attrib)
	    item.update({'xmltype':'item'})
	    item.update({'text':el.text})
	    catalog_ob['items'].append(item)
    return catalog_ob





class WitNewMap(Resource):
    def render_GET(self, request):
	# login_response = loginToNew()
	# login_response.addCallback(prepareNewRequest)
	# procs_done = login_response.addCallback(requestProcPage)
	# procs_done.addCallback(logoutFormNew)
        f = open('/home/aganzha/new.html')
        f.seek(0,2)
        parseNewPage(f,'procs')
	return "ok"




def logoutFormNew(headers):
    agent = Agent(reactor)
    agent.request('GET', "http://www.newsystem.ru/personal/auth.php?logout=yes&backurl=/goods-and-services/catalog/108/9438/index.php?IBLOCK_ID=108&SECTION_ID=9438",Headers(headers),None)
    print "_____________loggedOut"


class NewReceiver(Protocol):
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


# def parseNewPage(fileobj):
#     fileobj.seek(0)
#     c = fileobj.read()
#     f = open('/home/aganzha/new.html', 'w')
#     f.write(c)
#     fileobj.close()
#     f.close()
#     print ".."
#     print "done"

def getProcPage(response, further_d):
    for h in response.headers.getAllRawHeaders():
	if h[0] == 'Content-Encoding':
	    enc = h[1][0]
	    break
    response.deliverBody(NewReceiver(further_d, enc))

def requestProcPage(headers):
    agent = Agent(reactor)
    request_d = agent.request('GET', 'http://www.newsystem.ru/goods-and-services/catalog/108/9438/',Headers(headers),None)
    d = defer.Deferred()
    d.addCallback(parseNewPage, 'procs')
    request_d.addCallback(getProcPage, d)
    return request_d

class AuthProducer(object):
    implements(IBodyProducer)

    def __init__(self, login, password):
	self.body = u"backurl=/index.php&AUTH_FORM=Y&TYPE=AUTH&USER_LOGIN=%s&USER_PASSWORD=%s&Login=Авторизуйтесь" % (login, password)
	# self.body = quote_plus(self.body.encode('utf-8'))
	self.body = self.body.encode('utf-8')
	self.length = len(self.body)

    def startProducing(self, consumer):
	consumer.write(self.body)
	return succeed(None)

    def pauseProducing(self):
	pass

    def stopProducing(self):
	pass


def prepareNewRequest(login_response):
    headers = {}
    for k,v in standard_headers.items():
	if k == 'User-Agent':
	    headers.update({'User-Agent':[standard_user_agents[randint(0,len(standard_user_agents)-1)]]})
	else:
	    headers.update({k:v})
    raw = login_response.headers.getAllRawHeaders()
    for h in raw:
	if h[0] == 'Set-Cookie':
	    cookies = h[1]
	    break
    clean_cookies = []
    for c in cookies:
	clean_c = c.split(';')[0]
	clean_cookies.append(clean_c)
    if (len(clean_cookies) > 0):
	headers.update({'Cookie':[';'.join(clean_cookies)]})
    return headers


def loginToNew():
    url = 'http://www.newsystem.ru/personal/auth.php'
    login = new_user
    password = new_password
    agent = Agent(reactor)
    headers = {}
    for k,v in standard_headers.items():
	headers.update({k:v})
    producer = AuthProducer(login, password)
    headers.update({'Content-Type':['application/x-www-form-urlencoded; charset=UTF-8']})
    headers.update({'X-Requested-With':['XMLHttpRequest']})
    request_d = agent.request('POST', url,Headers(headers),producer)
    return request_d


def pr(res):
    print "pr"
    print res


def parseNewPage(f, external_id, remaining=None, parser=None):
    spoon = 1024*10
    if remaining is None:
        remaining = f.tell()
        # TODO! how do i know, that the received fileis more than 1024???
        parser=etree.HTMLParser(target=NewTarget())#encoding='cp1251'
        f.seek(0)
        rd = f.read(spoon)
        parser.feed(rd)
        remaining -= spoon
        d = deferLater(reactor, 0, parseNewPage, f, external_id, remaining, parser)
        return d
    else:
        if remaining < spoon:
            rd = f.read(remaining)
            parser.feed(rd)
            f.close()
            parser.close()
            di = parser.target
            print "yaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!"
            print di.components
            return defer.Deferred()
        else:
            rd = f.read(spoon)
            parser.feed(rd)
            remaining -= spoon
            d = deferLater(reactor, 0, parseNewPage, f, external_id, remaining, parser)
            return d



class NewTarget:    
    def makeDate(self):
        t = str(date.today())
        return t.split('-')


    def match(self, look_for, where_to_look):
        for k in look_for:
            if k not in where_to_look: return False
            if look_for[k] != where_to_look[k]: return False
        return True

    def end_of_tag(self, tag_match, params):
        return tag_match and 'end' in params

    def clean(self, txt):
        while True:
            if u"  " in txt:
                txt = txt.replace(u"  ", " ")
            else:
                break
        return txt.replace("\t", "").replace("\n", "")

    def __init__(self):
        self.components = []

    def walk(self):
        while True:
            params = yield
        # got_price = False
        # got_subj = False
        # got_text = False
        # got_fields = False
        # got_phone = False
        # passed_titles = 0
        # while True:
        #     params = yield
        #     if not got_price and self.match({'tag':'div', 'class':'price_box rounded'}, params):
        #         while not got_price:
        #             params = yield
        #             if self.match({'tag':'span'}, params):
        #                 while not got_price:
        #                     params = yield
        #                     if 'data' in params:
        #                         self.price += self.clean(params['data'])
        #                     else:
        #                         got_price = True
        #                         if u'\xd0' in self.price or u'\xd1' in self.price:
        #                             self.price = unicode(self.price.encode('raw-unicode-escape'), 'utf-8')
        #             if self.match({'tag':'div'}, params) and 'end' in params: got_price = True

        #     if not got_subj and self.match({'tag':'h3','class':'maintitle'},params):

        #         if passed_titles == 0:
        #             passed_titles +=1
        #         elif passed_titles == 1:
        #             while not got_subj:
        #                 params = yield
        #                 if 'data' in params:
        #                     self.subject += self.clean(params['data'])
        #                 else:
        #                     if u'\u2014' in self.subject:
        #                         self.subject = self.subject.split(u'\u2014')[1]
        #                     # while True:
        #                     #     if u"  " in self.subject:
        #                     #         self.subject = self.subject.replace(u"  ", " ")
        #                     #     else:
        #                     #         break

        #                     # tretiy3 UNICODE UTF-8 ENCODING LITERAL
        #                     if u'\xd0' in self.subject or u'\xd1' in self.subject:
        #                         self.subject = unicode(self.subject.encode('raw-unicode-escape'), 'utf-8')

        #                     passed_titles +=1
        #                     got_subj = True
        #         else:
        #             break


        #     if passed_titles == 2 and not got_text and self.match({'tag':'h3','class':'maintitle'},params):

        #         while not got_text:
        #             params = yield
        #             if self.match({'tag':'div'},params):
        #                 while not got_text:
        #                     params = yield
        #                     if 'data' in params:
        #                         self.text += self.clean(params['data'])
        #                     else:
        #                         got_text = True
        #                         passed_titles +=1

        #                         if u'\xd0' in self.text or u'\xd1' in self.text:
        #                             self.text = unicode(self.text.encode('raw-unicode-escape'), 'utf-8')

        #             if self.match({'tag':'div'}, params) and 'end' in params: got_text = True

        #     if passed_titles == 3 and not got_fields and self.match({'tag':'h3','class':'maintitle'},params):

        #         while not got_fields:
        #             params = yield
        #             if self.match({'tag':'div'},params):
        #                 while not got_fields:
        #                     params = yield
        #                     if self.match({'tag':'div'}, params) and 'end' in params:
        #                         got_fields = True
        #                         passed_titles +=1


        #                         break
        #                     if self.match({'tag':'p'},params):
        #                         key = ''
        #                         value =''
        #                         while True:
        #                             params = yield
        #                             if self.match({'tag':'b'}, params):
        #                                 # pass_b = False
        #                                 while True:
        #                                     params = yield

        #                                     if self.match({'tag':'b'}, params) and 'end' in params: break
        #                                     if 'data' in params:
        #                                         key += self.clean(params['data'])
        #                             if 'data' in params:
        #                                 value += self.clean(params['data'])
        #                             if self.match({'tag':'p'}, params) and 'end' in params:

        #                                 if u'\xd0' in key or u'\xd1' in key:
        #                                     key = unicode(key.encode('raw-unicode-escape'), 'utf-8')
        #                                 if u'\xd0' in value or u'\xd1' in value:
        #                                     value = unicode(value.encode('raw-unicode-escape'), 'utf-8')
        #                                 self.fields.update({key:value})
        #                                 break

        #     if passed_titles == 4 and not got_phone and self.match({'tag':'h3','class':'maintitle'},params):
        #         while not got_phone:
        #             params = yield
        #             if self.match({'tag':'div'}, params):
        #                 while not got_phone:
        #                     params = yield
        #                     # pass_p = False
        #                     if self.match({'tag':'div'}, params) and 'end' in params:
        #                         got_phone = True
        #                         passed_titles +=1
        #                         if u'\xd0' in self.phone or u'\xd1' in self.phone:
        #                             self.phone = unicode(self.phone.encode('raw-unicode-escape'), 'utf-8')


        #                     if self.match({'tag':'p'}, params):
        #                         while True:
        #                             params = yield
        #                             if self.match({'tag':'p'}, params) and 'end' in params:
        #                                 break
        #                             if 'data' in params:
        #                                 self.phone += self.clean(params['data'])

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
