# -*- coding: utf-8 -*-
from pc.secure import xml_source,xml_method, xml_login, xml_password
from lxml import etree
from twisted.python import log
import sys
import gzip
from twisted.web.xmlrpc import Proxy
import base64
from cStringIO import StringIO
from twisted.web.resource import Resource, ForbiddenResource
from pc.couch import couch
import simplejson
from twisted.internet import reactor
from twisted.web.client import Agent
from random import randint
from twisted.web.http_headers import Headers
from twisted.internet.protocol import Protocol
from twisted.internet import defer

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


class XmlGetter(Resource):
    def pr(self, fail):
        log.startLogging(sys.stdout)
        log.msg(fail)

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
        doc = simplejson.loads(raw_doc)
        need_store = False
        for k,v in doc.items():
            if k in item:
                if doc[k] != item[k]:
                    # TODO - treat changes here!
                    need_store = True
                    doc[k] = item[k]
        if need_store:
            d = couch.addAttachments(doc, raw_doc, version=True)
            d.addCallback(lambda _doc:couch.saveDoc(_doc))
            d.addErrback(self.pr)

    def getItem(self, res, gen):
        try:
            item = gen.next()
        except StopIteration:
            return
        sio = StringIO()
        item_code = item.pop('code')
        d = couch.openDoc(item_code, writer=sio)
        def co(res):
            self.compareItem(res, item, sio)
        def st(fail):
            if 'code' in item:
                c = couch.saveDoc(item, docId=item.pop('code'))
                c.addErrback(self.pr)
        d.addCallbacks(co,st)
        d.addErrback(self.pr)
        d.addCallback(self.getItem, gen)
        d.addErrback(self.pr)
        return d


    def compareDocs(self, res):
        src = base64.decodestring(res)
        sio = StringIO(src)
        gz = gzip.GzipFile(fileobj=sio)
        tree = etree.parse(gz)
        root = tree.getroot()
        gen = xmlToDocs([], root)
        self.getItem(None, gen)

    def render_GET(self, request):
        proxy = Proxy(xml_source)
        op = request.args.get('op', [None])[0]
        if op is not None:
            if op == 'store':
                proxy.callRemote(xml_method, xml_login, xml_password).addCallbacks(self.storeDocs, self.pr)
            elif op == 'compare':
                proxy.callRemote(xml_method, xml_login, xml_password).addCallbacks(self.compareDocs, self.pr)
            elif op == 'descr':
                self.storeDescription(request)
        return "ok"

    def storeDescription(self, request):
        _id = request.args.get('code')[0]
        _description = simplejson.loads(request.args.get('desription')[0][1:-1])
        d = couch.openDoc(_id)
        d.addCallback(self.saveDescription, _description)


    image_url = 'http://wit-tech.ru/img/get/file/'

    def saveDescription(self, doc, description):
        print "eeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        print doc['_id']
        if 'description' in doc:
            doc['description'] = description
        else:
            doc.update({'description':description})
        if 'imgs' not in doc['description']:
            couch.saveDoc(doc)
        else:
            print "will add images"            
            self.getImage(doc)

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
            print "--"
            print url
            d = defer.Deferred()
            image_request = agent.request('GET', url,Headers(headers),None)
            image_request.addCallback(lambda response: response.deliverBody(ImageReceiver(doc, img, d)))
            image_request.addErrback(self.pr)
            defs.append(d)
        li = defer.DeferredList(defs)
        li.addCallback(self.addImages, doc)
        li.addErrback(self.pr)
        return d

    def addImages(self, images, doc):
        print "addings!"
        attachments = {}
        for i in images:
            if i[0]:
                attachments.update(i[1])
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
        print "finishing!"
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
