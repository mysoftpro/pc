# -*- coding: utf-8 -*-
from cStringIO import StringIO
import gzip
from twisted.web.resource import Resource, ForbiddenResource
from twisted.web.static import File, getTypeAndEncoding
from twisted.internet import reactor, defer
from pc.jsmin import jsmin
from pc import base36
from twisted.web.server import NOT_DONE_YET
import os
from twisted.web.http import CACHED
from pc.couch import couch, designID
import simplejson
from datetime import datetime, date
from pc.models import index, computer, computers,parts,\
    noComponentFactory,makePrice,makeNotePrice,parts_names,parts,updateOriginalModelPrices,\
    BUILD_PRICE,INSTALLING_PRICE,DVD_PRICE,notebooks,lastUpdateTime, ZipConponents, CatalogsFor,\
    NamesFor, ParamsFor, promotion, findComponent, upgrade_set, Model
from pc.views import Cart
from pc.catalog import XmlGetter, WitNewMap
from twisted.web import proxy
from twisted.web.error import NoResource
from twisted.python.failure import Failure
from lxml import etree, html
from copy import deepcopy
from pc.mail import Sender, send_email
from pc.faq import faq, StoreFaq
from twisted.internet.task import deferLater
from pc.game import gamePage
from pc.payments import DOValidateUser,DONotifyPayment
from pc.di import Di
import sys
from pc.auth import OAuth, OpenId
from pc.common import addCookies, MIMETypeJSON

simple_titles = {
    '/howtochoose':u' Как выбирать компьютер',
    '/howtouse':u'Как пользоваться сайтом',
    '/howtobuy':u'Как покупать',
    '/warranty':u'Гарантии',
    '/support':u'Поддержка',
    '/about':u'Про магазин',
    '/whyauth':u'Зачем нужна авторизация',
    '/upgrade_set':u'Наборы для апгрейда',
}

def simplePage(template, skin, request):
    if request.path in simple_titles:
        title = skin.root().xpath('//title')[0]
        title.text = simple_titles[request.path]
    skin.top = template.top
    skin.middle = template.middle
    skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 190px;')
    skin.root().xpath('//div[@id="middle"]')[0].set('class','midlle_how')
    d = defer.Deferred()
    d.addCallback(lambda some:skin.render())
    d.callback(None)
    return d

parts_aliases = {
    'motherboard':('how_7388', u'Как выбирать материнскую плату'),
    'processor':('how_7399', u'Как выбирать процессор'),
    'video':('how_7396', u'Как выбирать видеокарту'),
    'hdd':('how_7394', u'Как выбирать жесткий диск'),
    'ram':('how_7369', u'Как выбирать память'),
    'case':('how_7387', u'Как выбирать корпус'),
    'display':('how_7390', u'Как выбирать монитор'),
    'keyboard':('how_7389', u'Как выбирать клавиатуру'),
    'mouse':('how_7383', u'Как выбирать мышь'),
    'audio':('how_7406', u'Как выбирать аудиосистему'),
}

def renderPartPage(doc, header, template, skin):
    container = template.middle.find('div')
    # try:
    els = html.fragments_fromstring(doc['html'])
    container.text = ''
    for el in els:
        if type(el) is unicode:
            container.text +=el
        else:
            container.append(el)
    template.top.find('h1').text = header
    title = skin.root().xpath('//title')[0]
    title.text = header
    skin.top = template.top
    skin.middle = template.middle
    # skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 230px;')
    # skin.root().xpath('//div[@id="middle"]')[0].set('style','margin-top: -90px;')
    return skin

def partPage(template, skin, request):
    name = request.path.split('/')[-1]
    d = couch.openDoc(parts_aliases[name][0])
    d.addCallback(renderPartPage, parts_aliases[name][1], template, skin)
    d.addCallback(lambda some:some.render())
    return d


static_hooks = {
    'index.html':index,
    'computer.html':computer,
    'computers.html':computers,
    'promotion.html':promotion,
    'howtochoose.html':simplePage,
    'howtouse.html':simplePage,
    'howtobuy.html':simplePage,
    'warranty.html':simplePage,
    'support.html':simplePage,
    'part.html':partPage,
    'notebook.html':notebooks,
    'faq.html':faq,
    'blog.html':faq,
    'game.html':gamePage,
    'payment_success.html':simplePage,
    'payment_fail.html':simplePage,
    'about.html':simplePage,
    'whyauth.html':simplePage,
    'upgrade_set.html':upgrade_set
    }



_cached_statics = {}

static_dir = os.path.join(os.path.dirname(__file__), 'static')




class SiteMap(Resource):
    def buildElement(self, location, freq="monthly", prior="0.8", today=None):
        url = etree.Element('url')
        loc = etree.Element('loc')
        loc.text = 'http://buildpc.ru/'+location
        lastmod = etree.Element('lastmod')
        if today is None:
            today = datetime.today()
        _mo = str(today.month)
        if (len(_mo))==1:
            _mo = "0"+_mo
        _da = str(today.day)
        if (len(_da))==1:
            _da = "0"+_da
        lastmod.text = '-'.join((str(today.year),_mo,_da))
        changefreq = etree.Element('changefreq')
        changefreq.text = freq
        priority = etree.Element('priority')
        priority.text = prior
        url.append(loc)
        url.append(lastmod)
        url.append(changefreq)
        url.append(priority)
        return url

    def siteMap(self, res, request):
        models = res[0][1]['rows']
        posts = res[1][1]['rows']
        faqs = res[2][1]['rows']
        request.setHeader('Content-Type', 'text/xml;charset=utf-8')
        root = etree.XML('<urlset></urlset>')
        root.set('xmlns',"http://www.sitemaps.org/schemas/sitemap/0.9")
        root.append(self.buildElement(''))
        root.append(self.buildElement('computer'))
        for model in models:
            root.append(self.buildElement('computer/'+model['key'], freq='daily'))
        for p in posts:
            if p['key'][1] != 'z': continue
            gd = lambda i: int(p['value'][i])
            n = datetime.today().replace(year=gd(0), month=gd(1),day=gd(2))
            root.append(self.buildElement('blog?key='+p['key'][0], freq='monthly', today=n))
        for p in faqs:
            if p['key'][1] != 'z': continue
            gd = lambda i: int(p['value'][i])
            n = datetime.today().replace(year=gd(0), month=gd(1),day=gd(2))
            root.append(self.buildElement('faq?key='+p['key'][0], freq='monthly', today=n))
        root.append(self.buildElement('blog'))
        root.append(self.buildElement('faq'))
        root.append(self.buildElement('about'))
        root.append(self.buildElement('whyauth'))
        root.append(self.buildElement('upgrade_set'))
        root.append(self.buildElement('howtochoose'))
        root.append(self.buildElement('howtobuy'))
        root.append(self.buildElement('howtouse'))
        root.append(self.buildElement('warranty'))
        root.append(self.buildElement('support'))
        root.append(self.buildElement('motherboard'))
        root.append(self.buildElement('video'))
        root.append(self.buildElement('processor'))
        root.append(self.buildElement('notebook'))

        root.append(self.buildElement('computer?cat=home'))
        root.append(self.buildElement('computer?cat=work'))
        root.append(self.buildElement('computer?cat=admin'))
        root.append(self.buildElement('computer?cat=game'))

        root.append(self.buildElement('/promotion/ajax'))

        request.write(etree.tostring(root, encoding='utf-8', xml_declaration=True))
        request.finish()

    def render_GET(self, request):
        d = couch.openView(designID, 'models')
        d1 = couch.openView(designID, 'blog')
        d2 = couch.openView(designID, 'faq')
        li = defer.DeferredList([d,d1,d2])
        li.addCallback(self.siteMap, request)
        return NOT_DONE_YET


class PriceForMarket(Resource):
    def prices(self, result, request):
        request.setHeader('Content-Type', 'text/xml;charset=utf-8')
        xml = '<!DOCTYPE yml_catalog SYSTEM "shops.dtd"><yml_catalog></yml_catalog>'
        tree = etree.parse(StringIO(xml))
        root = tree.getroot()
        # root = etree.XML('<yml_catalog></yml_catalog>')
        # tree = root.getroottree()
        # tree.docinfo.doctype = '<!DOCTYPE yml_catalog SYSTEM "shops.dtd">'
        # tree.DocInfo
        lut = lastUpdateTime()
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
        category.text = u'Ноутбуки Asus'
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
            url.text = 'http://buildpc.ru/notebook'
            offer.append(url)

            price = etree.Element('price')
            price.text = unicode(makeNotePrice(doc))
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
                    picture.text = 'http://buildpc.ru/image/'+doc['_id']+'/'+a
                    offer.append(picture)
                    break

            delivery = etree.Element('delivery')
            delivery.text = 'true'
            offer.append(delivery)

            _local_delivery_cost = etree.Element('local_delivery_cost')
            _local_delivery_cost.text = '0'
            offer.append(_local_delivery_cost)


            typePrefix = etree.Element('typePrefix')
            typePrefix.text = u'Ноутбук'
            offer.append(typePrefix)

            vendor = etree.Element('vendor')
            vendor.text = 'Asus'
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
        asus_12 = ["7362","7404","7586"]
        asus_14 = ["7362","7404","7495"]
        asus_15 = ["7362","7404","7468"]
        asus_17 = ["7362","7404","7704"]
        d = couch.openView(designID,'catalogs',include_docs=True,stale=False,
                           keys = [asus_12,asus_14,asus_15,asus_17])
        d.addCallback(self.prices, request)
        return NOT_DONE_YET



class Template(object):

    def __init__(self, opened_file, name_to_cache, last_modified):
        cache = globals()['_cached_statics']
        if name_to_cache in cache and cache[name_to_cache][0] == last_modified:
            self.tree = deepcopy(cache[name_to_cache][1])
        else:
            parser = etree.HTMLParser(encoding='utf-8')
            cache[name_to_cache] = (last_modified,etree.parse(opened_file, parser))
            self.tree = deepcopy(cache[name_to_cache][1])
        opened_file.close()

    def root(self):
        return self.tree.getroot().find('body')

    def render(self):
        return etree.tostring(self.tree, encoding='utf-8', method="html")


    def get_middle(self):
        return self.root().find('.//middle')

    def set_middle(self, middle):
        parent = self.get_middle().getparent()
        # REFACTOR
        div = etree.Element('div')
        div.set('id','middle')
        for el in middle:
            div.append(el)
        parent.replace(self.get_middle(), div)
        # parent.replace(self.get_middle(), middle)

    middle = property(get_middle, set_middle)


    def get_top(self):
        return self.root().find('.//top')

    def set_top(self, top):
        parent = self.get_top().getparent()
        # REFACTOR
        div = etree.Element('div')
        div.set('id','top')
        for el in top:
            div.append(el)
        parent.replace(self.get_top(), div)

    top = property(get_top, set_top)



class Skin(Template):
    def __init__(self):
        self.selected_skin = None
        cache = globals()['_cached_statics']
        name_to_cache = 'skin.html'
        if name_to_cache in cache:
            self.tree = deepcopy(cache[name_to_cache])
        else:
            opened_file = open(os.path.join(static_dir, name_to_cache))
            parser = etree.HTMLParser(encoding='utf-8')
            cache[name_to_cache] = etree.parse(opened_file, parser)
            self.tree = deepcopy(cache[name_to_cache])
            opened_file.close()


    skins = {'home':'/static/home.css'}

    def prepare(self, request):
        selected_skin = request.args.get('skin',[None])[0] or\
            request.getCookie('pc_skin')
        # if selected_skin is None: return
        if selected_skin in self.skins:
            self.selected_skin = selected_skin
            self.tree.getroot().find('head').find('link')\
                .set('href',self.skins[selected_skin])
            addCookies(request, {'pc_skin':selected_skin})
        else:
            addCookies(request, {'pc_skin':''})

    except_links = ['/rss']

    def render(self):
        if self.selected_skin is not None:
            logo = self.tree.getroot().find('body').xpath('//img[@id="logoImage"]')[0]
            logo.set('src', '/static/logo3.png')
        return etree.tostring(self.tree, encoding='utf-8', method="html")



class CachedStatic(File):

    def __init__(self, *args, **kwargs):
        self.skin = Skin()
        File.__init__(self, *args, **kwargs)
        self.hooks = {}

    def render(self, request):
        return self.render_GET(request)



    def render_GET(self, request):
        self.restat(False)

        if self.type is None:
            self.type, self.encoding = getTypeAndEncoding(self.basename(),
                                                          self.contentTypes,
                                                          self.contentEncodings,
                                                          self.defaultType)

        if 'image' in self.type:
            if hasattr(File, 'render_GET'):
                return File.render_GET(self, request)
            else:
                return File.render(self, request)

        if not self.exists():
            return self.childNotFound.render(request)

        if self.isdir():
            return self.redirect(request)

        request.setHeader('accept-ranges', 'bytes')


        try:
            fileForReading = self.openForReading()
        except IOError, e:
            import errno
            if e[0] == errno.EACCES:
                return ForbiddenResource().render(request)
            else:
                raise

        physical_name = fileForReading.name
        # virtual_name = unquote_plus(request.path.split('/')[-1])

        if 'jpg' in physical_name or 'gif' in physical_name or 'png' in physical_name or physical_name == 'jScrollPane.js':
            request.setHeader("Cache-Control", "max-age=290304000, public")
        else:
            request.setHeader("Cache-Control", "max-age=0, must-revalidate")#7200

        request.setHeader('Content-Encoding', 'gzip')

        if 'html' in self.type or 'text' in self.type:
            self.type += ';charset=utf-8'
        request.setHeader('Content-Type', self.type)
        last_modified = self.getmtime()
        # 304 is here
        physical_name_in_cache = physical_name in _cached_statics and _cached_statics[physical_name][0] == last_modified
        # virtual_name_in_cache = virtual_name in _cached_statics and _cached_statics[virtual_name][0] == last_modified

        if physical_name_in_cache and request.setLastModified(last_modified) is CACHED:
            return ''

        if physical_name_in_cache:
            return _cached_statics[physical_name][1]
        # if virtual_name_in_cache:
        #     return _cached_statics[virtual_name][1]

        else:
            if '.html' in fileForReading.name or '.json' in fileForReading.name:
                # name_to_cache = physical_name
                # DO NOT CACHE VIRTUAL NAMES. UNCOMMENT ALL TO CACHE EM
                # if len(virtual_name)>0:
                #     splitted = physical_name.split('\\')
                #     if len(splitted) == 0:
                #         splitted = physical_name.split('/')
                #     if splitted[-1] != virtual_name:
                #         name_to_cache = None # virtual_name
                d = self.renderTemplate(fileForReading, last_modified, request)
                d.addCallback(self._gzip, None, last_modified)
                d.addCallback(self.render_GSIPPED, request)
                #TODO! not just finish, but send email with error!
                # d.addErrback(lambda e:request.finish())
                return NOT_DONE_YET
            else:
                content = fileForReading.read()
                fileForReading.close()
                return self._gzip(content, physical_name, last_modified)



    def _gzip(self, _content,_name, _time):
        if _name is not None and "js" in _name and "min." not in _name:
            _content = jsmin(_content)
        buff = StringIO()
        f = gzip.GzipFile(_name,'wb',9, buff)
        f.write(_content)
        f.close()
        buff.seek(0)
        gzipped = buff.read()
        buff.close()
        if _name is not None:
            _cached_statics[_name] = (_time, gzipped)
        return gzipped



    def renderTemplate(self, fileForReading, last_modified, request):
        self.skin.prepare(request)
        short_name = None
        if '/' in fileForReading.name:
            short_name = fileForReading.name.split('/')[-1]
        else:
            short_name = fileForReading.name.split('\\')[-1]

        if short_name in static_hooks:
            template = Template(fileForReading,short_name,last_modified)
            d = static_hooks[short_name](template, self.skin, request)
        elif short_name in self.hooks:
            template = Template(fileForReading,short_name,last_modified)
            han = self.hooks[short_name]            
            renderrer = han.handler(template, self.skin, request, han.name)
            d = renderrer.render()
        else:
            # just an empty snippet
            d = defer.Deferred()
            content = fileForReading.read()
            d.addCallback(lambda x: content)
        fileForReading.close()
        return d

    def render_GSIPPED(self, gzipped, request):
        request.write(gzipped)
        request.finish()

class Cookable(Resource):
    def __init__(self):
        self.cookies = []
        Resource.__init__(self)

    def checkCookie(self, request):
        user_cookie = request.getCookie('pc_user')
        if  user_cookie is None:
            addCookies(request, {'pc_user':base36.gen_id()})

_comet_users = {}

class Root(Cookable):
    def __init__(self, host_url, index_page):
        Cookable.__init__(self)
        self.static = CachedStatic(static_dir)
        self.static.indexNames = [index_page]
        self.putChild('static',self.static)
        self.putChild('computer', TemplateRenderrer(self.static, 'computers.html','computer.html'))
        self.putChild('cart', TemplateRenderrer(self.static, 'computers.html','computers.html'))

        self.putChild('cart1', PCTemplateRenderrer(Cart, self.static, 'cart.html'))

        self.putChild('computer', TemplateRenderrer(self.static, 'computers.html','computer.html'))
        self.putChild('promotion', TemplateRenderrer(self.static, 'promotion.html','promotion.html'))
        self.putChild('notebook', TemplateRenderrer(self.static, 'notebook.html'))
        self.putChild('howtochoose', TemplateRenderrer(self.static, 'howtochoose.html'))
        self.putChild('howtouse', TemplateRenderrer(self.static, 'howtouse.html'))
        self.putChild('howtobuy', TemplateRenderrer(self.static, 'howtobuy.html'))
        self.putChild('warranty', TemplateRenderrer(self.static, 'warranty.html'))
        self.putChild('support', TemplateRenderrer(self.static, 'support.html'))
        self.putChild('motherboard', TemplateRenderrer(self.static, 'part.html'))
        self.putChild('processor', TemplateRenderrer(self.static, 'part.html'))
        self.putChild('video', TemplateRenderrer(self.static, 'part.html'))
        self.putChild('ram', TemplateRenderrer(self.static, 'part.html'))
        self.putChild('hdd', TemplateRenderrer(self.static, 'part.html'))
        self.putChild('ram', TemplateRenderrer(self.static, 'part.html'))
        self.putChild('case', TemplateRenderrer(self.static, 'part.html'))
        self.putChild('display', TemplateRenderrer(self.static, 'part.html'))
        self.putChild('keyboard', TemplateRenderrer(self.static, 'part.html'))
        self.putChild('mouse', TemplateRenderrer(self.static, 'part.html'))
        self.putChild('audio', TemplateRenderrer(self.static, 'part.html'))
        self.putChild('faq', TemplateRenderrer(self.static, 'faq.html'))
        self.putChild('blog', TemplateRenderrer(self.static, 'faq.html'))
        self.putChild('storefaq', StoreFaq())
        self.putChild('xml',XmlGetter())
        self.putChild('map',WitNewMap())
        self.putChild('component', Component())
        self.putChild('image', ImageProxy())
        self.putChild('save', Save())
        self.putChild('savemodel', ModelSave())
        self.putChild('savenote', SaveNote())
        self.putChild('delete',Delete())
        self.putChild('deleteNote',DeleteNote())
        self.putChild('deleteAll',DeleteAll())
        self.putChild('sender', Sender())
        # self.putChild('select_helps', SelectHelpsProxy())
        from pc.admin import Admin
        self.putChild('admin',Admin())
        self.host_url = host_url
        self.putChild('5406ae5f1ec4.html',File(os.path.join(static_dir,'5406ae5f1ec4.html')))
        self.putChild('sitemap.xml',SiteMap())
        self.putChild('robots.txt',File(os.path.join(static_dir,'robots.txt')))
        self.putChild('receiver.html',File(os.path.join(static_dir,'_receiver.html')))
        self.putChild('comet', Comet())
        self.putChild('modeldesc', ModelDesc())
        self.putChild('prices_for_market',PriceForMarket())
        # self.putChild('game', TemplateRenderrer(self.static, 'game.html'))
        self.putChild('modelstats', ModelStats())
        self.putChild('do_validate_user', DOValidateUser())
        self.putChild('do_notify_payment', DONotifyPayment())
        self.putChild('zip_components', ZipConponents())
        self.putChild('catalogs_for',CatalogsFor())
        self.putChild('names_for', NamesFor())
        self.putChild('params_for', ParamsFor())
        self.putChild('do_payment_success',TemplateRenderrer(self.static, 'payment_success.html'))
        self.putChild('do_payment_fail',TemplateRenderrer(self.static, 'payment_fail.html'))
        self.putChild('about',TemplateRenderrer(self.static, 'about.html'))
        self.putChild('whyauth',TemplateRenderrer(self.static, 'whyauth.html'))
        self.putChild('rss', Rss())
        self.putChild('fromBlog', FromBlog())
        self.putChild('di',Di())
        self.putChild('checkModel', CheckModel())
        self.putChild('store_cart_comment',StoreCartComment())
        self.putChild('store_model_name', StoreModelName())
        self.putChild('bill.pdf', PdfBill())
        self.putChild('oauth',OAuth())
        self.putChild('openid',OpenId())
        self.putChild('upgrade_set',TemplateRenderrer(self.static, 'upgrade_set.html'))

    def getChild(self, name, request):
        self.checkCookie(request)
        u = str(request.URLPath())
        if ('http://' + self.host_url + '/' == u) or 'favicon' in name:
            return self.static.getChild(name, request)
        return self




class PdfBill(Resource):
    def done(self, data, request):
        request.setHeader('Content-Type', 'application/pdf')
        request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
        request.write(data)
        request.finish()

    def renderNote(self, doc, request):
        def render(user):
            if 'notebooks' in user and doc['_id'] in user['notebooks']:
                def addNote(note):
                    note['price'] = makeNotePrice(note)
                    doc['items'] = {'notebook':note['_id']}
                    doc['full_items'] = [note]
                    doc['const_prices'] = [DVD_PRICE, BUILD_PRICE, INSTALLING_PRICE]
                    d = self.spawn(doc)
                    d.addCallback(self.done, request)
                    return d
                n = couch.openDoc(user['notebooks'][doc['_id']])
                n.addCallback(addNote)
                return n
            request.write('fail')
            request.finish()
        user = couch.openDoc(request.getCookie('pc_user'))
        user.addCallback(render)

    def spawn(self, doc):
        from pc import pdf
        d = defer.Deferred()
        writer = pdf.PdfWriter(simplejson.dumps(doc), d)
        _file = pdf.__file__
        if _file.endswith('pyc'):
            _file = _file[:-1]
        path = sys.executable
        reactor.spawnProcess(writer, path, [path, '-u', _file])
        return d

    def renderBill(self, doc, request):
        if not 'items' in doc:
            # may be notebook or component
            return self.renderNote(doc, request)
        model = Model(doc)
        d = self.spawn(model.preparePdf())
        d.addCallback(self.done, request)


    def render_GET(self, request):
        _id = request.args.get('id', [None])[0]
        if _id is None:
            return "ok"
        d = couch.openDoc(_id)
        d.addCallback(self.renderBill, request)
        return NOT_DONE_YET

class StoreModelName(Resource):
    def store(self, doc_user, name, title, key):
        if not doc_user[0][0] or not doc_user[1][0]: return
        doc = doc_user[0][1]
        user = doc_user[1][1]
        if doc['author'] == user['_id'] and key == user['pc_key']:
            need_save = False
            if len(name)>0:
                doc['name'] = name
                need_save = True
            if len(title)>0:
                doc['title'] = title
                need_save = True
            if need_save:
                couch.saveDoc(doc)

    def render_GET(self, request):
        uuid = request.args.get('uuid', [None])[0]
        name = request.args.get('name', [''])[0]
        title = request.args.get('title', [''])[0]
        user = request.getCookie('pc_user')
        key = request.getCookie('pc_key')
        if uuid is not None and (len(name)>0 or len(title)>0):
            d = couch.openDoc(uuid)
            d1 = couch.openDoc(user)
            defer.DeferredList([d,d1]).addCallback(self.store, name,title, key)
        return "ok"

class StoreCartComment(Resource):
    def finish(self, doc, request):
        comment = {'email':request.args.get('email',[''])[0],
                   'author':request.args.get('name',[request.getCookie('pc_user')])[0],
                   'body':request.args.get('txt',[''])[0],
                   'date':str(date.today()).split('-')}
        if 'comments' in doc:
            doc['comments'].append(comment)
        else:
            doc['comments'] = [comment]
        couch.saveDoc(doc)
        # zzz
        send_email('inbox@buildpc.ru',
                   u'Комментарий в корзине',
                   'http://buildpc.ru/cart/'+doc['author']+' '+doc['_id'],
                   sender=u'Компьютерный магазин <admin@buildpc.ru>')
        request.write("ok")
        request.finish()

    def render_POST(self, request):
        _id = request.args.get('_id', [None])[0]
        if _id is None: return "fail"
        d =couch.openDoc(_id)
        d.addCallback(self.finish, request)
        return NOT_DONE_YET

class CheckModel(Resource):
    def notify(self, res, author):
        send_email('inbox@buildpc.ru',
                   u'Требуется проверить конфигурацию',
                   'http://buildpc.ru/cart/'+author+' http://buildpc.ru/computer/'+res['id'] +' http://buildpc.ru/admin/couch/_utils/document.html?pc/'+res['id'],
                   sender=u'Компьютерный магазин <admin@buildpc.ru>')

    def checkModel(self, doc, request):
        doc['checkModel'] = False
        d = couch.saveDoc(doc)
        d.addCallback(self.notify, request.getCookie('pc_user'))
        request.write("done")
        request.finish()

    def render_GET(self, request):
        uuid = request.args.get('uuid',[None])[0]
        if uuid is None:
            return "ok"
        d = couch.openDoc(uuid)
        d.addCallback(self.checkModel, request)
        return NOT_DONE_YET


class FromBlog(Resource):
    def __init__(self, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.blog_proxy = proxy.ReverseProxyResource('127.0.0.1', 5984, '/pc/_design/pc/_view/blog', reactor=reactor)
        self.faq_proxy = proxy.ReverseProxyResource('127.0.0.1', 5984, '/pc/_design/pc/_view/faq', reactor=reactor)

    @MIMETypeJSON
    def render_GET(self, request):
        proxy = self.blog_proxy
        if 'faq' in request.getHeader('Referer'):
            proxy = self.faq_proxy
        return proxy.render(request)


class ModelStats(Resource):
    def render_GET(self, request):
        _id = request.args.get('id',[None])[0]
        if _id is not None:
            d = couch.openDoc(_id)
            def incr(doc):
                if 'hits' in doc:
                    doc['hits']=doc['hits']+1
                else:
                    doc['hits'] = 1
                couch.saveDoc(doc)
            d.addCallback(incr)
        return "ok"


class ModelDesc(Resource):
    def finish(self, doc, request):
        res = {}
        if 'modeldesc' in doc:
            res.update({'modeldesc':doc['modeldesc']})
        if 'hits' in doc:
            res.update({'hits':doc['hits']})
        request.write(simplejson.dumps(res))
        # request.write(doc['modeldesc'].encode('utf-8'))
        request.finish()

    def finishHitsOnly(self, result, request):
        res = {}
        for r in result['rows']:
            doc = r['doc']
            if 'hits' in doc:
                res.update({'m'+doc['_id']:doc['hits']})
            else:
                res.update({'m'+doc['_id']:1})
        request.write(simplejson.dumps(res))
        request.finish()

    @MIMETypeJSON
    def render_GET(self, request):
        _id = request.args.get('id', [None])[0]
        if _id is not None:
            d = couch.openDoc(_id)
            d.addCallback(self.finish, request)
            d.addErrback(lambda x: request.finish())
            return NOT_DONE_YET
        hitsonly = request.args.get('hitsonly', [None])[0]
        if hitsonly is not None:
            d = couch.openView(designID,'models',include_docs=True,stale=False)
            d.addCallback(self.finishHitsOnly, request)
            d.addErrback(lambda x: request.finish())
            return NOT_DONE_YET
        request.finish()

class Comet(Resource):
    def finish(self, request, user):
        if user in globals()['_comet_users']:
            globals()['_comet_users'].pop(user)
        request.write('fail')
        request.finish()

    def fail(self, err, call, user):
        if user in globals()['_comet_users']:
            globals()['_comet_users'].pop(user)
        call.cancel()
    def render_GET(self, request):
        user = request.getCookie('pc_user')
        if user not in globals()['_comet_users']:
            globals()['_comet_users'].update({user:request})
        call = reactor.callLater(60, self.finish, request, user)
        request.notifyFinish().addErrback(self.fail, call, user)
        return NOT_DONE_YET


class HandlerAndName(object):
    def __init__(self, handler, name):
        self.handler = handler
        self.name = name

        

class PCTemplateRenderrer(Cookable):
    def __init__(self, klass, static, name):
        Cookable.__init__(self)
        self.static = static
        self.name = name
        self.klass = klass

    def render_GET(self, request):
        return NoResource().render(request)

    def getChild(self, name, request):
        child = self.static.getChild(self.name, request)
        child.hooks.update({self.name:HandlerAndName(self.klass, name)})
        return child


class TemplateRenderrer(Cookable):
    def __init__(self, static, name, default_name=None, title=None):
        Cookable.__init__(self)
        self.static = static
        self.name = name
        self.default_name = default_name

    def render_GET(self, request):
        self.checkCookie(request)
        return self.static.getChild(self.name, request).render_GET(request)

    def getChild(self, name, request):
        self.checkCookie(request)
        child = None
        if self.default_name is None:
            child = Cookable.getChild(self, self.name,request)
        else:
            child = self.static.getChild(self.default_name, request)
        return child







class CustomWriter(object):
    def __init__(self, viewName):
        self.strio = StringIO()
        self.gzipfile = gzip.GzipFile(viewName, 'wb', 9, self.strio)

    def write(self, data):
        self.gzipfile.write(data)
    def read(self):
        self.gzipfile.close()
        return self.strio.getvalue()

    def close(self):
        self.strio.close()


class Component(Resource):
    isLeaf = True
    allowedMethods = ('GET',)
    def writeComponent(self, doc, request):
        descr = {'name':'','comments':'','img':[],'imgs':[]}
        if 'description' in doc:
            descr = doc['description']
        price = makePrice(doc)
        descr['price'] = price
        request.write(simplejson.dumps(descr))
        request.finish()

    @MIMETypeJSON
    def render_GET(self, request):
        _id = request.args.get('id', [None])[0]
        if _id is None: return simplejson.dumps({'name':'','comments':'','img':[],'imgs':[]})
        if 'no' in _id: return simplejson.dumps({'name':'','comments':'','img':[],'imgs':[]})
        d = couch.openDoc(_id)
        d.addCallback(self.writeComponent, request)
        return NOT_DONE_YET



class Save(Resource):
    def finish(self, user_model, request, user_doc):
        if user_model[0][0] and user_model[1][0]:
            in_cart = len(user_doc['models'])
            if 'notebooks' in user_doc:
                in_cart+=len(user_doc['notebooks'].keys())
            addCookies(request, {'pc_cart':str(in_cart)})
            request.write(simplejson.dumps(user_model[1][1]))
        else:
            request.write(simplejson.dumps({}))
        request.finish()

    @MIMETypeJSON
    def render_GET(self, request):
        model = request.args.get('model', [None])[0]
        if model is not None:
            jmodel = simplejson.loads(model)
            # TODO validate fields to avoid hacks!
            user_id = request.getCookie('pc_user')
            if user_id is None:
                user_id = base36.gen_id()
            d1 = couch.openDoc(user_id)
            d2 = defer.Deferred()
            model_id = None
            if 'id' in jmodel:
                model_id = jmodel.pop('id')
                d2 = couch.openDoc(model_id)
            else:
                model_id = base36.gen_id()
                d2.addCallback(lambda x: jmodel)
                d2.callback(None)
            li = defer.DeferredList([d1,d2])
            li.addCallback(self.saveModel, user_id, model_id, jmodel, request)
            return NOT_DONE_YET
        return 'fail'

    # TODO! how fast is base36.gen_id() ???? may be wrap in deferred???
    def saveModel(self, user_model, user_id, model_id, new_model, request):
        from pc import models
        user_doc = None
        if user_model[0][0]:
            user_doc = user_model[0][1]
        else:
            user_doc = {'_id':user_id, 'models':[], 'pc_key':base36.gen_id()}
            addCookies(request, {'pc_key':user_doc['pc_key']})
        model_doc = None
        if user_model[1][0]:
            edit_model = request.args.get('edit', [None])[0] is not None
            if edit_model:
                same_author = user_model[1][1]['author'] == user_id and \
                'pc_key' in user_doc and \
                request.getCookie('pc_key') == user_doc['pc_key']
                not_processing = not 'processing' in user_model[1][1] \
                    or not user_model[1][1]['processing']
                if same_author and not_processing:
                    model_doc = user_model[1][1]
                else:
                    model_doc = new_model
                    model_doc['_id'] = model_id
            else:
                model_doc = new_model
                model_doc['_id'] = model_id
        else:
            model_doc = new_model
            model_doc['_id'] = model_id

        # no it does not matter what we have in model_doc.
        # brand new or existant model. just copy all fron new model here
        for k,v in new_model.items():
            model_doc[k] = v
        model_doc['original_prices'] = {}
        for name,code in model_doc['items'].items():
            if type(code) is list:
                code = code[0]
            if code in models.gChoices_flatten:
                component = models.gChoices_flatten[code]
                model_doc['original_prices'].update({code:component['price']})
            else:
                model_doc['original_prices'].update({code:0})

        model_doc['author'] = user_id
        if model_doc['_id'] not in user_doc['models']:
            user_doc['models'].append(model_doc['_id'])
        _date=str(date.today()).split('-')
        user_doc['date'] = _date
        model_doc['date'] = _date
        d1 = couch.saveDoc(user_doc)
        d2 = couch.saveDoc(model_doc)
        li = defer.DeferredList([d1,d2])
        li.addCallback(self.finish, request,user_doc)




class ModelSave(Save):
    def render_GET(self, request):
        model = request.args.get('model', [None])[0]

        if model is not None:
            # jmodel = simplejson.loads(model)
            user_id = request.getCookie('pc_user')
            d1 = couch.openDoc(user_id)
            d2 = couch.openDoc(model)
            model_id = base36.gen_id()
            li = defer.DeferredList([d1,d2])
            def fake_new_model(list_res):
                catalog_model = list_res[1][1]
                catalog_model.pop('_id')
                catalog_model.pop('_rev')
                catalog_model.pop('_attachments')
                catalog_model.pop('ours')
                return self.saveModel(list_res, user_id,model_id,catalog_model, request)
            li.addCallback(fake_new_model)
            return NOT_DONE_YET
        return 'fail'


class SaveNote(Resource):
    def finish(self, res, note_id, request):
        request.write(note_id)
        request.finish()
    def fail(self, fail, request):
        request.write('fail')
        request.finish()

    def addNote(self, user_doc, _id, request):
        _date=str(date.today()).split('-')
        user_doc['date'] = _date
        note_id = base36.gen_id()
        if 'notebooks' in user_doc:
            user_doc['notebooks'].update({note_id:(_id)})
        else:
            user_doc['notebooks'] = {note_id:(_id)}
        in_cart = len(user_doc['models']) + len(user_doc['notebooks'].keys())
        addCookies(request, {'pc_cart':str(in_cart)})
        couch.saveDoc({'_id':note_id, 'author':user_doc['_id'], 'building':False,'dvd':False,'installing':False})
        return note_id


    def oldUser(self, user_doc, _id, request):
        note_id = self.addNote(user_doc, _id, request)
        d = couch.saveDoc(user_doc)
        d.addCallback(self.finish, note_id, request)
        d.addErrback(self.fail, request)
        return d

    def newUser(self, fail, user_id, _id, request):
        user_doc = {'_id':user_id, 'models':[], 'pc_key':base36.gen_id()}
        addCookies(request, {'pc_key':user_doc['pc_key']})
        note_id = self.addNote(user_doc, _id, request)
        d = couch.saveDoc(user_doc)
        d.addCallback(self.finish, note_id, request)
        d.addErrback(self.fail, request)
        return d

    def render_GET(self, request):
        _id = request.args.get('id', [None])[0]
        if _id is None:
            return 'fail'
        user_id = request.getCookie('pc_user')
        d = couch.openDoc(user_id)
        d.addCallback(self.oldUser, _id, request)
        d.addErrback(self.newUser, user_id, _id, request)
        return NOT_DONE_YET

def get_uuid():
    d = defer.Deferred()
    d.addCallback(lambda some: base36.gen_id())
    d.callback(None)
    return d

class Delete(Resource):
    def render_GET(self, request):
        uuid = request.args.get('uuid', [None])[0]
        user_id = request.getCookie('pc_user')
        model = couch.openDoc(uuid)
        user = couch.openDoc(user_id)
        def delete(user_model):
            if not user_model[0][0] or not user_model[1][0]:
                request.write('fail')
                request.finish()
                return
            _user = user_model[0][1]
            _model = user_model[1][1]
            same_author = _model['author'] == _user['_id'] and \
                'pc_key' in _user and\
                request.getCookie('pc_key') == _user['pc_key']
            not_processing = not 'processing' in _model \
                    or not _model['processing']
            if same_author and not_processing:
                couch.deleteDoc(uuid,_model['_rev'])
                _user['models'] = [m for m in _user['models'] if m != _model['_id']]
                in_cart = len(_user['models'])
                if 'notebooks' in _user:
                    in_cart+=len(_user['notebooks'].keys())
                addCookies(request, {'pc_cart':str(in_cart)})
                couch.saveDoc(_user)
                request.write('ok')
                request.finish()
            request.write('fail')
            request.finish()
        defer.DeferredList([user,model]).addCallback(delete)
        return NOT_DONE_YET


class DeleteNote(Resource):
    def render_GET(self, request):
        uuid = request.args.get('uuid', [None])[0]
        user_id = request.getCookie('pc_user')
        user = couch.openDoc(user_id)
        def delete(_user):
            if 'pc_key' in _user \
                    and request.getCookie('pc_key') == _user['pc_key']\
                    and 'notebooks' in _user\
                    and uuid in _user['notebooks']:
                _user['notebooks'].pop(uuid)
                in_cart = len(_user['models'])
                if 'notebooks' in _user:
                    in_cart+=len(_user['notebooks'].keys())
                addCookies(request, {'pc_cart':str(in_cart)})
                couch.saveDoc(_user)
                request.write('ok')
                request.finish()
            request.write('fail')
            request.finish()
        user.addCallback(delete)
        return NOT_DONE_YET





class DeleteAll(Resource):

    def finish(self, some, request):
        addCookies(request, {'pc_user':'','pc_key':'','pc_cart':'','pc_cookie_forced':''})
        request.write('ok')
        request.finish()

    def deleteAll(self, models, user_doc,request):
        defs = []
        for row in models['rows']:
            if not 'doc' in row:
                continue
            doc = row['doc']
            if doc is None:
                continue
            if 'processing' in doc and doc['processing']:continue
            defs.append(couch.deleteDoc(doc['_id'],doc['_rev']))
        if len(defs) == len(models['rows']):
            couch.deleteDoc(user_doc['_id'],user_doc['_rev'])
        self.finish(None, request)

    def render_GET(self, request):
        user_id = request.getCookie('pc_user')
        user = couch.openDoc(user_id)
        def delete(user_doc):
            d = defer.Deferred()
            if 'pc_key' in user_doc and request.getCookie('pc_key') == user_doc['pc_key']:
                d = couch.listDoc(keys=user_doc['models'], include_docs=True)
                d.addCallback(self.deleteAll, user_doc, request)
            else:
                d.addCallback(self.finish, request)
                d.callback(None)
            return d
        user.addCallback(delete)
        return NOT_DONE_YET



# http://localhost:5984/pc/18060/L0JlbnFfbGNkL1Y5MjAuanBn.jpg
class ImageProxy(Resource):
    def __init__(self, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.proxy = proxy.ReverseProxyResource('127.0.0.1', 5984, '/pc', reactor=reactor)

    def getChild(self, path, request):
        last = request.uri.split('/')[-1]

        # safety to not show couch internals
        # just check that it endswith image extension and no parameters in it
        if '?' in last or '&' in last:
            return NoResource().render(request)
        image = last.endswith('.jpg')
        image = image or last.endswith('.jpeg')
        image = image or last.endswith('.png')
        image = image or last.endswith('.gif')

        if not image:
            return NoResource().render(request)

        return self.proxy.getChild(path, request)

class Rss(Resource):
    def __init__(self, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.proxy = proxy.ReverseProxyResource('127.0.0.1', 5984, '/pc/_design/pc/_list/rss/rss?descending=true&limit=20', reactor=reactor)
    def render_GET(self, request):
        return self.proxy.render(request)

# class SelectHelpsProxy(Resource):
#     def __init__(self, *args, **kwargs):
#       Resource.__init__(self, *args, **kwargs)
#       self.proxy = proxy.ReverseProxyResource('127.0.0.1', 5984, '/pc', reactor=reactor)

#     def getChild(self, path, request):
#       last = request.uri.split('/')[-1]

#       # safety to not show couch internals
#       # just check that it endswith image extension and no parameters in it
#       if '?' in last or '&' in last:
#           return NoResource()
#       _help = 'how_' in last
#       if not _help:
#           return NoResource()
#       return self.proxy.getChild(last, request)
