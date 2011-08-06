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
                couch.saveDoc(item, docId=item.pop('code'))                
        d.addCallbacks(co,st)
        d.addCallback(self.getItem, gen)
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
        return "ok"

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
