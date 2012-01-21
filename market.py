# -*- coding: utf-8 -*-
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from pc.catalog import standard_headers, standard_user_agents, downloadPage, NewTarget, Comparator
from random import randint
from twisted.internet import defer
import re
from urllib import quote_plus
from lxml import etree
from twisted.internet.task import deferLater
from pc.couch import couch, designID
from twisted.web.resource import Resource
from cStringIO import StringIO
from twisted.web.server import NOT_DONE_YET
from pc.models import Model

class PriceForMarket(Resource):
    def prices(self, result, request):
        request.setHeader('Content-Type', 'text/xml;charset=utf-8')
        xml = '<!DOCTYPE yml_catalog SYSTEM "shops.dtd"><yml_catalog></yml_catalog>'
        tree = etree.parse(StringIO(xml))
        root = tree.getroot()
        from pc.views import Index
        lut = Index.lastUpdateTime()
        da,ta = lut.split(' ')
        lida = da.split('.')
        lida.reverse()
        da = '-'.join(lida)
        root.set('date', da+' '+ta)

        shop = etree.Element('shop')

        name = etree.Element('name')
        name.text = 'buildpc.ru'
        shop.append(name)

        company = etree.Element('company')
        company.text = u'ИП Ганжа А.Ю.'
        shop.append(company)

        url = etree.Element('url')
        url.text = 'http://buildpc.ru'
        shop.append(url)


        currencies = etree.Element('currencies')
        currency = etree.Element('currency')
        currency.set('id','RUR')
        currency.set('rate','1')
        currency.set('plus','0')

        currencies.append(currency)
        shop.append(currencies)

        categories = etree.Element('categories')
        category  = etree.Element('category')
        category.set('id','2')
        category.text = u'Видеокарты'
        categories.append(category)
        shop.append(categories)
        local_delivery_cost = etree.Element('local_delivery_cost')
        local_delivery_cost.text ="0"
        shop.append(local_delivery_cost)

        offers = etree.Element('offers')
        for r in result['rows']:
            if 'doc' not in r: continue
            doc = r['doc']
            if doc is None: continue
            offer = etree.Element('offer')
            offer.set('id', doc['_id'])

            offer.set('type',"vendor.model")
            offer.set('available',"true")

            url = etree.Element('url')
            url.text = 'http://buildpc.ru/videocard/'+quote_plus(r['key'])
            offer.append(url)

            price = etree.Element('price')
            price.text = unicode(Model.makePrice(doc))
            offer.append(price)

            currencyId = etree.Element('currencyId')
            currencyId.text = 'RUR'
            offer.append(currencyId)

            categoryId = etree.Element('categoryId')
            categoryId.set('type','Own')
            categoryId.text = "2"
            offer.append(categoryId)

            for a in doc['_attachments']:
                if doc['_attachments'][a]['content_type']=="image/jpeg":
                    picture = etree.Element('picture')
                    picture.text = 'http://buildpc.ru/image/'+doc['_id']+'/'+quote_plus(a)
                    offer.append(picture)
                    break

            delivery = etree.Element('delivery')
            delivery.text = 'true'
            offer.append(delivery)

            _local_delivery_cost = etree.Element('local_delivery_cost')
            _local_delivery_cost.text = '0'
            offer.append(_local_delivery_cost)


            typePrefix = etree.Element('typePrefix')
            typePrefix.text = u'Видеокарта'
            offer.append(typePrefix)

            vendor = etree.Element('vendor')
            vendor.text = doc['vendor']
            offer.append(vendor)

            model = etree.Element('model')
            model.text = doc['text']
            offer.append(model)

            available = etree.Element('available')
            available.text = 'true'

            manufacturer_warranty = etree.Element('manufacturer_warranty')
            manufacturer_warranty.text = doc['warranty_type']
            offer.append(manufacturer_warranty)
            offers.append(offer)

        shop.append(offers)
        root.append(shop)
        request.write(etree.tostring(tree, encoding='utf-8', xml_declaration=True))
        request.finish()

    def render_GET(self, request):
        # asus_12 = ["7362","7404","7586"]
        # asus_14 = ["7362","7404","7495"]
        # asus_15 = ["7362","7404","7468"]
        # asus_17 = ["7362","7404","7704"]
        # d = couch.openView(designID,'catalogs',include_docs=True,stale=False,
        #                    keys = [asus_12,asus_14,asus_15,asus_17])
        d = couch.openView(designID,'video_articul',include_docs=True,stale=False)
        d.addCallback(self.prices, request)
        return NOT_DONE_YET






def parseMarket(f, url='url', remaining=None, parser=None):
    spoon = 1024*10
    if remaining is None:
        remaining = f.tell()
        parser=etree.HTMLParser(encoding='utf-8')
        f.seek(0)
        rd = f.read(spoon)
        parser.feed(rd)
        remaining -= spoon
        d = deferLater(reactor, 0, parseMarket, f, url, remaining, parser)
        return d
    else:
        if remaining < spoon:
            rd = f.read(remaining)
            parser.feed(rd)
            f.close()
            root = parser.close()
            all_divs = []
            for i in xrange(3):
                klass = 'comment left'+str(i)
                if not 'forums' in url:
                    klass = "b-grade " + klass
                divs = root.xpath('//div[@class="'+klass+'"]')
                for d in divs:
                    td = d.xpath('//td[@class="b-grade__feedback grade-opinion-actions"]')
                    for t in td:
                        t.getparent().remove(t)
                    imgs = d.xpath('//img[@class="b-rating__icon"]')
                    for i in imgs:
                        i.getparent().remove(i)

                all_divs+=divs
            globals()['gMarket_Cached'][url] = all_divs
            return all_divs
        else:
            rd = f.read(spoon)
            parser.feed(rd)
            remaining -= spoon
            d = deferLater(reactor, 0, parseMarket, f, url, remaining, parser)
            return d



gMarket_Cached = {}

def getMarket(card):
    cached = globals()['gMarket_Cached']
    if card.marketComments in cached and card.marketReviews in cached:
        d1 = defer.Deferred()
        d1.addCallback(lambda x: cached[card.marketComments])
        d1.callback(None)
        d2 = defer.Deferred()
        d2.addCallback(lambda x: cached[card.marketReviews])
        d2.callback(None)
        return defer.DeferredList((d1,d2))

    agent = Agent(reactor)
    headers = {}
    for k,v in standard_headers.items():
        if k == 'User-Agent':
            headers.update({'User-Agent':[standard_user_agents[randint(0,len(standard_user_agents)-1)]]})
        else:
            headers.update({k:v})

    c = defer.Deferred()
    c.addCallback(parseMarket, url=card.marketComments)
    r = defer.Deferred()
    r.addCallback(parseMarket, url=card.marketReviews)


    request_comments = agent.request('GET', str(card.marketComments),Headers(),None)
    request_comments.addCallback(downloadPage, c)
    request_reviews = agent.request('GET', str(card.marketReviews),Headers(),None)
    request_reviews.addCallback(downloadPage, r)
    return defer.DeferredList((c,r))
