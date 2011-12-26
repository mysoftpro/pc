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
from datetime import date
from pc import models
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
		# reset stock for wit components                
                if 'doc' in row:
                    row['doc']['stock1'] = 0
                    couch.saveDoc(row['doc'])
                    deleted_count +=1
	# destroy cache here!
	from pc import admin
	admin.clear_cache()
	send_email('admin@buildpc.ru',
		   u'Обновление wit-tech',
		   u'Всего позиций:' + unicode(all_count) + u', удалено позиций:' + unicode(deleted_count),
		   sender=u'Компьютерный магазин <inbox@buildpc.ru>')

    def getItem(self, res, gen, codes):
	try:
	    item = gen.next()
	except StopIteration:
	    # separate view
	    _all = couch.openView(designID,'wit_codes',stale=False) #couch.listDoc()
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

    def imgReceiverFactory(self, d, img):#doc,  ??
	def factory(response):
	    response.deliverBody(ImageReceiver(img+'.jpg', d))# doc, ??
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
	    image_request.addCallback(self.imgReceiverFactory(d, img))# doc, img, 
	    image_request.addErrback(self.pr)
	    defs.append(d)
	li = defer.DeferredList(defs)
	li.addCallback(self.addImages, doc)
	li.addErrback(self.pr)
	return li

    def addImages(self, images, doc):
	attachments = {}
	for i in images:
	    if i[0]:
		attachments.update(i[1])
	d = couch.addAttachments(doc, attachments)
	d.addCallback(lambda _doc:couch.saveDoc(_doc))
	d.addErrback(self.pr)

class ImageReceiver(Protocol):
    def __init__(self, name, finish):#doc ??
        # ????
	# self.doc = doc
	self.name = name
	self.file = StringIO()
	self.finish = finish

    def dataReceived(self, bytes):
	self.file.write(bytes)

    def connectionLost(self, reason):
	self.file.seek(0,2)
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
    new_places = {
	'http://www.newsystem.ru/goods-and-services/catalog/108/9438/':'procs',
	'http://www.newsystem.ru/goods-and-services/catalog/108/9426/':'mothers',
	'http://www.newsystem.ru/goods-and-services/catalog/108/9475/':'videos',
	'http://www.newsystem.ru/goods-and-services/catalog/108/9689/':'exclusive_cases',
        'http://www.newsystem.ru/goods-and-services/catalog/108/9420/':'game_cases',
        'http://www.newsystem.ru/goods-and-services/catalog/108/9422/':'simple_cases',
        'http://www.newsystem.ru/goods-and-services/catalog/108/9463/':'sata_disks',
        'http://www.newsystem.ru/goods-and-services/catalog/108/9450/':'ram',
        'http://www.newsystem.ru/goods-and-services/catalog/84/9032/':'soft'
        }
    def goForNew(self, headers):
	defs = []
	for k,v in self.new_places.items():
	    defs.append(requestNewPage(headers,k,v))
	li = defer.DeferredList(defs)
	return li.addCallback(lambda x: headers)

    def render_GET(self, request):
	key = request.args.get('key', [None])[0]
	if key is None or key != xml_key:
	    return "fail"
	login_response = loginToNew()
	login_response.addCallback(prepareNewRequest)
	all_done = login_response.addCallback(self.goForNew)
	all_done.addCallback(logoutFromNew)
	return "ok"




def logoutFromNew(headers):
    agent = Agent(reactor)
    agent.request('GET', "http://www.newsystem.ru/personal/auth.php?logout=yes&backurl=/goods-and-services/catalog/108/9438/index.php?IBLOCK_ID=108&SECTION_ID=9438",Headers(headers),None)


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


def downloadPage(response, further_d):
    for h in response.headers.getAllRawHeaders():
	if h[0] == 'Content-Encoding':
	    enc = h[1][0]
	    break
    response.deliverBody(NewReceiver(further_d, enc))

def requestNewPage(headers, url, external_id):
    agent = Agent(reactor)
    request_d = agent.request('GET', url,Headers(headers),None)
    d = defer.Deferred()
    d.addCallback(parseNewPage, external_id)
    request_d.addCallback(downloadPage, d)
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
	    return parser.target.prepareNewComponents(external_id)
	else:
	    rd = f.read(spoon)
	    parser.feed(rd)
	    remaining -= spoon
	    d = deferLater(reactor, 1, parseNewPage, f, external_id, remaining, parser)
	    return d



class Comparator():
    def __init__(self, params):
	self.params = params
    def cattr(self, at):
	return at in self.params
    def eattr(self, at,value, condition=lambda x,y: x==y):
	return condition(self.params[at],value)

    #TODO! refactor parseNewPage!!!!!!!!!!!!!!!!! it is fucke UGLY
    def tag(self, name):
	return 'tag' in self.params and self.params['tag'] == name

    def klass(self, name):
	return 'class' in self.params and self.params['class'] == name

    def _id(self, name):
	return 'id' in self.params and self.params['id'] == name

    def data(self):
	return 'data' in self.params


class NewTarget:
    def makeDate(self):
	t = str(date.today())
	return t.split('-')


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
	self.walker = self.walk()
	self.walker.next()

    def walk(self):
	while True:
	    params = yield
	    comp = Comparator(params)
	    if comp.cattr('tag') and comp.eattr('tag','tr')\
		    and comp.cattr('id') and comp.eattr('id','bx_', lambda x,y:x.startswith(y)):
		component = {'_id':'new_'+params['id'].split('_')[-1]}
		# print "get tr"
		finish_component = False
		while not finish_component:
		    params = yield
		    comp = Comparator(params)
		    if comp.cattr('tag') and comp.eattr('tag','td')\
			    and comp.cattr('class') and comp.eattr('class','catalog-list-item'):
			# print "first td"
			# first td here it is possible extract image
			while not finish_component:
			    params = yield
			    comp = Comparator(params)
			    if comp.cattr('tag') and comp.eattr('tag','td')\
				    and comp.cattr('class') and \
				    comp.eattr('class','catalog-list-item'):
				# print "second td"
				# second td
				# here wil be the 'a' with link to component .it is possible
				# extract catalogs from it!
				component['spans'] = []
				while not finish_component:
				    params = yield
				    comp = Comparator(params)
				    if comp.cattr('tag') and comp.eattr('tag','a') \
					    and comp.cattr('start'):
					component['new_link'] = params['href']
					while True:
					    params = yield
					    comp = Comparator(params)
					    if comp.cattr('data'):
						if 'text' in component:
						    component['text']+=params['data']
						else:
						    component['text']=params['data']
					    else:
						break

				    if comp.cattr('tag') and comp.eattr('tag','table') and comp.cattr('end'):
					# print "finish"
					# brak here cause get end of tr. but htm is broken, so use table instead!
					finish_component = True
					self.components.append(component)
					# print component
					break
				    if comp.cattr('tag') and comp.eattr('tag','span')\
					    and comp.cattr('start'):
					# here are spans with the price!
					# print "span!"
					while not finish_component:
					    params = yield
					    comp = Comparator(params)
					    if comp.cattr('data'):
						# print "data!"
						# print params['data'].encode('utf-8')
						component['spans'].append(params['data'])
					    else:
						break


    def start(self, tag, attrib):
	params = {'tag':tag, 'start':'start'}
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

    number_pat = re.compile(unicode("[0-9]*", 'utf-8'), re.UNICODE)
    rur_price_pat = re.compile(unicode("[0-9\.\,]*", 'utf-8'), re.UNICODE)
    us_price_pat = re.compile(unicode('\(([0-9\.\,]*)', 'utf-8'), re.UNICODE)


    def storeNewComponent(self, c):
	def store(err):
	    d = couch.saveDoc(c)
            d.addCallback(lambda x: c['_id'])
            return d
	return store

    def updateComponent(self, c):
	def update(doc):
            need_save = False
	    for k,v in c.items():
		if doc[k] != v:
                    doc[k] = v
                    need_save = True
            if 'price' in doc:
                doc['price'] = c['us_price']
            if 'stock1' in doc:
                doc['stock1'] = c['new_stock']
            if need_save:
                d = couch.saveDoc(doc)
                d.addCallback(lambda x: c['_id'])
                return d
            else:
                return c['_id']
	return update


    def cleanNewDocs(self, some):
        print "yaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        print some

    def prepareNewComponents(self, external_id):
	defs = []
	for c in self.components:
	    if c['spans'][-1]==u'в наличии':
		c['new_stock'] = 5
	    else:
		try:
		    ma = re.match(self.number_pat,c['spans'][-1])
		    if ma is not None:
			c['new_stock'] = int(ma.group())
		except:
		    c['new_stock'] = 0
	    try:
		rur_price = re.match(self.rur_price_pat,c['spans'][0])\
		    .group().replace('.','').replace(',','.')
		us_price = re.match(self.us_price_pat,c['spans'][1])\
		    .groups()[0].replace('.','').replace(',','.')
		rur_recommended_price = re.match(self.rur_price_pat,c['spans'][2])\
		    .group().replace('.','').replace(',','.')
		us_recommended_price = re.match(self.us_price_pat,c['spans'][3])\
		    .groups()[0].replace('.','').replace(',','.')
		c['rur_price'] = round(float(rur_price))
		c['us_price'] = round(float(us_price),2)
		c['rur_recommended_price'] = round(float(rur_recommended_price))
		c['us_recommended_price'] = round(float(us_recommended_price),2)
		c.pop('spans')
		c['new_catalogs'] = external_id
                d = couch.openDoc(c['_id'])
		d.addCallback(self.updateComponent(c))
		d.addErrback(self.storeNewComponent(c))
		defs.append(d)
	    except:
		pass
	li = defer.DeferredList(defs)
	li.addCallback(self.cleanNewDocs)
        li.addCallback(lambda x: send_email('admin@buildpc.ru',
					    u'Обновление new system '+external_id,
					    u'Всего позиций:' + unicode(len(defs)),
					    sender=u'Компьютерный магазин <inbox@buildpc.ru>'))
	return li


proc_fm1 = "9588"
proc_am23 = "9713"
proc_am23_ = "9439"
proc_1155 = "9440"
proc_1156 = "9441"
proc_775 = "9443"
mother_am23 = "9703"
mother_am23_ = "9427"
mother_1156 = "9712"
mother_fm1="9428"
mother_1155="9429"
mother_775 = "9432"

new_catalogs_mapping = {
    proc_fm1:models.proc_fm1,
    proc_am23:models.proc_am23,
    proc_am23_:models.proc_am23,
    proc_1155:models.proc_1155,
    proc_1156:models.proc_1156,
    proc_775:models.proc_775,
    mother_am23:models.mother_am23,
    mother_am23_:models.mother_am23,
    mother_1156:models.mother_1156,
    mother_fm1:models.mother_fm1,
    mother_1155:models.mother_1155,
    mother_775:models.mother_775
    }



def parseNewDescription(f, external_id, remaining=None, parser=None):
    spoon = 1024*10
    if remaining is None:
	remaining = f.tell()
	# TODO! how do i know, that the received fileis more than 1024???
	parser=etree.HTMLParser(target=NewDescriptionTarget())#encoding='cp1251'
	f.seek(0)
	rd = f.read(spoon)
	parser.feed(rd)
	remaining -= spoon
	d = deferLater(reactor, 0, parseNewDescription, f, external_id, remaining, parser)
	return d
    else:
	if remaining < spoon:
	    rd = f.read(remaining)
	    parser.feed(rd)
	    f.close()
	    parser.close()
	    return parser.target.prepareDescription(external_id)
	else:
	    rd = f.read(spoon)
	    parser.feed(rd)
	    remaining -= spoon
	    d = deferLater(reactor, 0, parseNewDescription, f, external_id, remaining, parser)
	    return d


class NewDescriptionTarget(NewTarget):

    def __init__(self):
	self.name = u''
	self.image = u''
	self.tds = []
	self.description = ''
	self.collect = False
	self.walker = self.walk()
	self.walker.next()


    def prepareDescription(self, external_id):
        warranty = ''
        articul = ''
        pairs = ''
        for pair in self.tds:
            if u'Гарантия' in pair[0]:
                warranty = pair[1]
            elif u'Артикул' in pair[0]:
                articul = pair[1]
            else:
                pairs+= u' '.join(pair)
            [u' '.join(pair) for pair in self.tds]
        return simplejson.dumps({'descr':self.description+pairs,
                                 'name':self.name,
                                 'img':self.image,
                                 'warranty':warranty,
                                 'articul':articul})
                                 
                                 
    def walk(self):
	while True:
	    params = yield
	    comp = Comparator(params)
	    if comp.tag('div') and comp.klass('catalog-element'):
		while True:
		    params = yield
		    comp = Comparator(params)
		    if 'data' in params and self.collect:
                        if u'Назад в раздел' in params['data']:
                            self.collect = False
                        else:
                            self.description += params['data']
		    if comp.tag('h1'):
			while True:
			    params = yield
			    if 'data' in params:
				self.name+=params['data']
			    else:
				break
		    if comp.tag('div') and comp._id('picture'):
			while True:
			    params = yield
			    comp = Comparator(params)
			    if comp.tag('img'):
				self.image = params['src']
				# print "iiiiiiiiiiiiiiiiiiiiiimage"
				# print self.image
				break

		    if comp.tag('table') and comp.klass('data-table'):
			tds = []
			while True:
			    params = yield
			    comp = Comparator(params)
			    if comp.tag('tr') and 'start' in params:
				while True:
				    params = yield
				    comp = Comparator(params)
				    if comp.tag('td') and 'start' in params:
					while True:
					    params = yield
					    comp = Comparator(params)
					    if 'data' in params:
						if len(tds)==0:
						    tds.append([params['data']])
						else:
						    if len(tds[-1])==2:
							tds.append([params['data']])
						    else:
							tds[-1].append(params['data'])
					    elif comp.tag('b') and 'start' in params:
						    while True:
							params = yield
							if 'data' in params:
							    if len(tds)==0:
								tds.append([params['data']])
							    else:
								if len(tds[-1])==2:
								    tds.append([params['data']])
								else:
								    tds[-1].append(params['data'])
							else:
							    break
					    else:
						break
				    else:
					self.tds = tds
					break
			    elif comp.tag('table') and 'end' in params:
                                self.collect = True
                                # print "exit table"
				# print self.tds
				break


def goForNewDescription(headers, url, d):
    agent = Agent(reactor)
    request_d = agent.request('GET', url,Headers(headers),None)
    request_d.addCallback(downloadPage, d)
    return request_d


def getNewDescription(link):

    login_response = loginToNew()
    login_response.addCallback(prepareNewRequest)
    
    d = defer.Deferred()
    d.addCallback(parseNewDescription, 'description')
    
    login_response.addCallback(goForNewDescription, 'http://www.newsystem.ru'+link, d)
    login_response.addCallback(logoutFromNew)
    
    return d






# def newImgReceiverFactory(self, img, d):
#     def factory(response):
#         response.deliverBody(ImageReceiver(img,d))
#     return factory


def getNewImage(res, img):
    url = ''
    if 'upload' in img:
        url = 'http://newsystem.ru/upload'+img.split('upload')[-1]
    else:
        url = 'http://newsystem.ru'+img

    agent = Agent(reactor)
    headers = {}

    for k,v in standard_headers.items():
        if k == 'User-Agent':
            headers.update({'User-Agent':[standard_user_agents[randint(0,len(standard_user_agents)-1)]]})
        else:
            headers.update({k:v})
    
    d = defer.Deferred()
    image_request = agent.request('GET', str(url),Headers(headers),None)
    image_request.addCallback(lambda response: response.deliverBody(ImageReceiver(img,d)))
    image_request.addErrback(pr)
    d.addCallback(addNewImage, res['id'])
    d.addErrback(pr)
    return d

def addNewImage(image, _id):
    def add(doc):
        d = couch.addAttachments(doc, image)#image is a dictionary
        d.addCallback(lambda _doc:couch.saveDoc(_doc))
        d.addErrback(pr)
    d = couch.openDoc(_id)
    d.addCallback(add)    
