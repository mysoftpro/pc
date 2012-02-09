# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from lxml import etree, html
from twisted.internet import defer
import simplejson
import re
from copy import deepcopy
from urllib import unquote_plus, quote_plus
from datetime import datetime,timedelta, date
from pc.mail import send_email
from twisted.web.resource import Resource
from pc.common import MIMETypeJSON
from pc import base36
from random import randint

BUILD_PRICE = 800
INSTALLING_PRICE=800
DVD_PRICE = 800
NOTE_MARGIN=1500
TABLET_MARGIN=800

gWarning_sent = []

components = "7363"
perifery = "7365"


proc = "7399"
mother = "7388"

mother_1155 = [components, mother,"17961"]#
mother_1156 = [components,mother,"12854"]#
mother_1366 =[components,mother,"18029"]#
mother_775 = [components,mother,"7449"]#
mother_am23 = [components,mother,"7699"]#
mother_fm1 = [components,mother,"19238"]#

video = "7396"

geforce = [components,video,"7607"]
radeon = [components,video,"7613"]

ram = "7394"
ddr3 = [components, ram, "11576"]
ddr2 = [components, ram, "7711"]
so_dim = [components, ram,"16993"]

hdd = "7406"
satas = [components, hdd,"7673"]
ides = [components, hdd,"7564"]

case = "7383"
case_400_650 = [components,case,"7459"]
case_exclusive = [components,case, "10837"]

displ = "7384"
displ_19_20 = [components,displ,"7526"]
displ_22_26 = [components,displ,"13209"]


kbrd = "7387"
kbrd_a4 = [perifery,kbrd,"14092"]
kbrd_acme = [perifery,kbrd,"7593"]
kbrd_chikony = [perifery,kbrd,"17396"]
kbrd_game = [perifery,kbrd,"18450"]


mouse = "7390"
mouse_a4 = [perifery,mouse,"7603"]
mouse_genius = [perifery,mouse,"15844"]
mouse_acme = [perifery,mouse,"14320"]
mouse_game = [perifery,mouse,"7582"]

sound = "7413"
sound_internal = [components,sound,"8012"]

network = "7405"
lan = [network,"14710"]

proc_1155 = [components, proc, "18027"]#
proc_1156 = [components,proc,"18028"]#
proc_1366 = [components,proc,"9422"]#
proc_775 = [components,proc,"7451"]#
proc_am23 = [components,proc,"7700"]#
proc_fm1 =  [components,proc,"19257"]#

audio = "7389"
audio_20 = [perifery,audio, "7447"]
audio_21 = [perifery,audio, "7448"]
audio_51 = [perifery,audio, "7462"]

soft = "7369"
microsoft = "14570"
windows = [soft,microsoft,"14571"]
psu = "7416"
power = [components,psu,"7464"]

notes_and_descktops = "7362"
notes = "7404"
asus_12 = [notes_and_descktops,notes,"7586"]
asus_14 = [notes_and_descktops,notes,"7495"]
asus_15 = [notes_and_descktops,notes,"7468"]
asus_17 = [notes_and_descktops,notes,"7704"]
tablet = "19220"
tablets = [notes_and_descktops,notes,tablet]


network = "7405"
routers = "7551"
edimax_routers = [network,routers,"15090"]
digitus_routers = [network,routers,"19931"]
dlink_routers = [network,routers,"12980"]


flash = "13710"
micro_sd = "7407"
flash_micro_sd = [flash,micro_sd]

mother_to_proc_mapping= [(mother_1155,proc_1155),
                         (mother_1156,proc_1156),
                         (mother_1366,proc_1366),
                         (mother_775,proc_775),
                         (mother_am23,proc_am23),
                         (mother_fm1,proc_fm1)]




Margin=1.15
Course = 30.5

#refactor (just comment it and youl see
def cleanDoc(doc, price, clean_text=True, clean_description=True):
    new_doc = {}
    to_clean = ['id', '_attachments','flags','inCart',
                     'ordered','reserved','stock1', '_rev', 'warranty_type',
                'articul', 'rur_price','us_price','us_recommended_price', 'rur_recommended_price',
                'new_stock', 'new_link', 'new_catalogs', "marketComments","marketParams",
                "marketReviews", "description"]
    if clean_text:
        to_clean.append('text')
    if ('sli' in doc and 'crossfire' in doc and 'ramslots' not in doc and 'stock1' in doc) and \
            (doc['sli']>0 or doc['crossfire']>0) and doc['stock1']<=1:
        to_clean.append('sli')
        to_clean.append('crossfire')
    for token in doc:
        if token in to_clean:
            continue
        if token == 'catalogs':
            new_doc.update({token:Model.getCatalogsKey(doc)})
        else:
            new_doc.update({token:doc[token]})
    new_doc['price'] = price
    return new_doc


parts = {mother:0, proc:10, video:20, hdd:30, ram:40,
         case:50, displ:90,
         audio:100, soft:110,
         kbrd:120, mouse:130, audio:140, psu:150, notes:160, routers:170, tablet:180}

parts_names = {proc:u'Процессор', ram:u'Память',
               video:u'Видеокарта', hdd:u'Жесткий диск', case:u'Корпус',
               sound:u'Звуковая карта',
               network:u'Сетевая карта',
               mother:u'Материнская плата',displ:u'Монитор',
               audio:u'Аудиосистема', kbrd:u'Клавиатура', mouse:u'Мышь',
               soft:u'ОС', psu:u'Блок питания', notes:u'Ноутбуки',
               routers:u'Маршрутизаторы',tablet:u'Планшет'}


parts_aliases = {
    'ram':ram,
    'mother':mother,
    'proc':proc,
    'video':video,
    'kbrd':kbrd,
    'mouse':mouse,
    'audio':audio,
    'sound':sound,
    'hdd':hdd,
    'displ':displ,
    'network':network,
    'soft':soft,
    'case':case,
    'psu':psu,
    'notes':notes,
    'router':routers,
    'tablet':tablet
    }

def noComponentFactory(_doc, name, text=u' нет'):
    no_name = 'no' + name
    no_doc = deepcopy(_doc)
    no_doc['_id'] = no_name
    no_doc['price'] = 0
    if name == psu:
        no_doc['text']=u'Блок питания встроенный в корпус'
    else:
        no_doc['text'] = parts_names[name]+text
    return no_doc


no_component_added = False


from twisted.python import log
import sys

def pr(some):
    log.startLogging(sys.stdout)
    log.msg(some)
    return some



gChoices = None
gChoices_flatten = {}

def noChoicesYet():
    return globals()['gChoices'] is not None




font_pat_1 = '<font[^>]*>[^<]*</font>'
font_pat_2 = '<font[^>]*>'

def cleanFlattenChoice(doc):
    def _pop(name):
        if 'descriptions' in doc and name in doc['descriptions']:
            doc['descriptions'].pop(name)
    _pop('img')
    _pop('name')
    _pop('comments')
    doc['text'] = re.sub(font_pat_1,'',doc['text'])
    doc['text'] = re.sub(font_pat_2,'',doc['text'])


def flatChoices(res):
    for name,choices in globals()['gChoices'].items():
        if type(choices) is list:
            for el in choices:
                if el[0]:
                    for ch in el[1][1]['rows']:
                        cleanFlattenChoice(ch['doc'])
                        globals()['gChoices_flatten'][ch['doc']['_id']] = ch['doc']
        else:
            for ch in choices['rows']:
                cleanFlattenChoice(ch['doc'])
                globals()['gChoices_flatten'][ch['doc']['_id']] = ch['doc']




def openChoicesView(key,name=None):
    d = None
    if type(key[0]) is list:
        d = couch.openView(designID,'catalogs',include_docs=True, keys=key, stale=False)
    else:
        d = couch.openView(designID,'catalogs',include_docs=True, key=key, stale=False)
    if name is not None:
        d.addCallback(lambda res: (name,res))
    return d


def fillChoices():
    _gChoices = globals()['gChoices']
    if _gChoices is not None:
        d = defer.Deferred()
        d.addCallback(lambda x: _gChoices)
        d.callback(None)
        return d
    defs = []
    # omit LGA 1366, LGA 775, LGA1156, LGA1166
    defs.append(defer.DeferredList([openChoicesView(mother_1155,"LGA1155"),
                                    openChoicesView(mother_am23,"AM2 3"),
                                    openChoicesView(mother_fm1,"FM1")])
                .addCallback(lambda res: {mother:res}))


    defs.append(defer.DeferredList([openChoicesView(proc_1155,'LGA1155'),
                                    openChoicesView(proc_am23,'AM2 3'),
                                    openChoicesView(proc_fm1, "FM1")])
                .addCallback(lambda res: {proc:res}))

    defs.append(defer.DeferredList([openChoicesView(geforce,u"GeForce"),
                                    openChoicesView(radeon,u"Radeon")])
                .addCallback(lambda res: {video:res}))

    defs.append(openChoicesView(ddr3)
                .addCallback(lambda res: {ram:res}))
    defs.append(openChoicesView(satas)
                .addCallback(lambda res: {hdd:res}))
    defs.append(openChoicesView(windows)
                .addCallback(lambda res: {soft:res}))

    defs.append(defer.DeferredList([openChoicesView(case_400_650,u"Корпусы 400-650 Вт"),
                                    openChoicesView(case_exclusive, u"Эксклюзивные корпусы")])
                .addCallback(lambda res: {case:res}))

    defs.append(defer.DeferredList([openChoicesView(displ_19_20,u"Мониторы 19-20 дюймов"),
                                    openChoicesView(displ_22_26,u"Мониторы 22-26 дюймов")])
                .addCallback(lambda res: {displ:res}))


    defs.append(defer.DeferredList([openChoicesView(kbrd_a4, u"Клавиатуры A4Tech"),
                                    openChoicesView(kbrd_acme,u"Клавиатуры Acme"),
                                    openChoicesView(kbrd_chikony,u"Клавиатуры Chikony"),
                                    openChoicesView(kbrd_game,u"Игровые Клавиатуры")])
                .addCallback(lambda res: {kbrd:res}))

    # openChoicesView(mouse_a4, u"Мыши A4Tech"),
    defs.append(defer.DeferredList([openChoicesView(mouse_game, u"Игровые Мыши"),
                                    openChoicesView(mouse_acme, u"Мыши Acme"),
                                    openChoicesView(mouse_genius, u"Мыши Genius")])
                .addCallback(lambda res: {mouse:res}))

    defs.append(defer.DeferredList([openChoicesView(audio_20,u"Аудио системы 2.0"),
                                    openChoicesView(audio_21,u"Аудио системы 2.1"),
                                    openChoicesView(audio_51,u"Аудио системы 5.1")])
                .addCallback(lambda res: {audio:res}))

    defs.append(defer.DeferredList([openChoicesView(power,u"Блоки питания")])
                .addCallback(lambda res: {psu:res}))

    defs.append(openChoicesView([asus_12,asus_14,asus_15,asus_17])
                .addCallback(lambda res: {notes:res}))
    
    defs.append(openChoicesView([tablets])
                .addCallback(lambda res: {tablet:res}))

    defs.append(openChoicesView([digitus_routers,dlink_routers,edimax_routers])
                .addCallback(lambda res: {routers:res}))

    defs.append(openChoicesView([flash_micro_sd])
                .addCallback(filterSd)
                .addCallback(lambda res: {micro_sd:res}))

    return defer.DeferredList(defs).addCallback(makeDict).addCallback(fillNew)


def makeDict(res):
    new_res = {}
    for el in res:
        if el[0]:
            new_res.update(el[1])
    globals()['gChoices'] = new_res
    flatChoices(new_res)
    return globals()['gChoices']


def filterSd(res):
    res['rows'] = [r for r in res['rows'] if len(r.get('doc',{}).get('description',{}))>0]
    return res
    

def fillNew(global_choices):
    def fill(res):
        for row in res['rows']:
            wit_doc = globals()['gChoices_flatten'][row['key']]
            if wit_doc['price']>row['value'][0]:
                wit_doc['price'] = row['value'][0]
            wit_doc['stock1'] = row['value'][1]
    d = couch.openView(designID, 'new_map', keys = globals()['gChoices_flatten'].keys())
    d.addCallback(fill)
    d.addCallback(lambda some: global_choices)
    return d



model_categories = {'home':['storage','spline','shade'],
                    'work':['localhost','scroll','chart'],
                    'admin':['ping','cell','compiler'],
                    'game':['zoom','render','raytrace']}

model_categories_titles = {'home':u'Домашние компьютеры',
                           'work':u'Компьюетры для работы',
                           'admin':u'Компьютеры для айтишников',
                           'game':u'Игровые компьютеры'}



class ZipConponents(Resource):

    def getPriceAndCode(self, row):
        #Component(
        return {row['doc']['_id']:Model.makePrice(row['doc'])}

    @MIMETypeJSON
    def render_GET(self, request):
        mothers = []
        procs = []
        videos = []
        for sockets in globals()['gChoices'][mother]:
            mothers.append(sockets[1][1]['rows'])
        for sockets in globals()['gChoices'][proc]:
            procs.append(sockets[1][1]['rows'])
        for sockets in globals()['gChoices'][video]:
            for r in sockets[1][1]['rows']:
                videos.append(self.getPriceAndCode(r))

        mothers_mapping = {}
        for m in mothers:
            if len(m)==0:continue
            cats = Model.getCatalogsKey(m[0]['doc'])
            mothers_mapping.update({tuple(cats):m})
        proc_mapping = {}
        for p in procs:
            if len(p)==0:continue
            cats = Model.getCatalogsKey(p[0]['doc'])
            proc_mapping.update({tuple(cats):p})
        mother_procs = []
        for tu in mother_to_proc_mapping:
            tm = tuple(tu[0])
            tp = tuple(tu[1])
            if  tm in mothers_mapping and tp in proc_mapping:
                mother_procs.append([[self.getPriceAndCode(c) for c in mothers_mapping[tm]],
                                     [self.getPriceAndCode(c) for c in proc_mapping[tp]]])

        return simplejson.dumps({'mp':mother_procs,'v':videos})


class CatalogsFor(Resource):

    @MIMETypeJSON
    def render_GET(self, request):
        codes = request.args.get('c',[])
        if len(codes)==0:
            request.finish()
        res = {}
        for c in codes:
            res.update({c:Model.getCatalogsKey(globals()['gChoices_flatten'][c])})
        return simplejson.dumps(res)


class NamesFor(Resource):
    @MIMETypeJSON
    def render_GET(self, request):
        codes = request.args.get('c',[])
        if len(codes)==0:
            request.finish()
        res = {}
        for c in codes:
            component = globals()['gChoices_flatten'][c]
            res.update({c:component['text'] + ' <strong>'+unicode(Model.makePrice(component)) + u' р</strong>'})
        return simplejson.dumps(res)

class ParamsFor(Resource):
    @MIMETypeJSON
    def render_GET(self, request):
        _type = request.args.get('type',[None])[0]
        if _type is None:
            return "ok"
        codes = request.args.get('c',[])
        if len(codes)==0:
            request.finish()
        res = {}
        for c in codes:
            component = globals()['gChoices_flatten'][c]
            if _type == 'proc':
                res.update({c:
                            {'brand':component['brand'] if 'brand' in component else '',
                            'cores':component['cores'] if 'cores' in component else '',
                            'cache':component['cache'] if 'cache' in component else ''}
                            })
        return simplejson.dumps(res)

def renderPromotion(doc, template, skin):
    template.top.find('h1').text = doc['name']
    stuff = template.middle.xpath('//table[@id="promostuff"]')[0]
    record = template.root().find('record')

    def setImage(img, src):
        img.set('src','/image/'+doc['_id']+'/'+src)
    components = {}
    for c in sorted(doc['components'],lambda x,y:x['order']-y['order']):
        rec = deepcopy(record)
        tr = rec.find('tr')
        tds = tr.findall('td')
        tds[0].find('img').set('src','/static/promotion/'+c['type']+'.png');
        tds[-1].text = c['name']
        tr.set('id', c['code'])
        stuff.append(tr)
        if c['order'] == 10:
            i = template.middle.xpath('//div[@id="promo_image"]')[0].find('img')
            setImage(i,c['top_image'])
            desc = template.middle.xpath('//div[@id="promo_description"]')[0]
            p = etree.Element('p')
            p.text = c['description']
            desc.append(p)
            if 'bottom_images' in c:
                for i in c['bottom_images']:
                    img = etree.Element('img')
                    setImage(img,i)
                    p.append(img)
        components.update({c['code']:c})

    scr = template.middle.find('script')
    scr.text = 'var _id="'+doc['_id']+'";var components='+simplejson.dumps(components)+';'
    scr.text += 'var parts = ' + simplejson.dumps(parts_aliases) + ';'
    template.top.xpath('//div[@id="promo_title"]')[0].text = doc['title']
    template.top.xpath('//div[@id="promo_extra"]')[0].text = doc['extra']
    descr = template.top.xpath('//p[@id="promo_desc"]')[0]
    for el in html.fragments_fromstring(doc['description']):
        descr.append(el)
    template.top.xpath('//div[@id="pprice"]')[0].text = unicode(doc['our_price'])

    skin.top = template.top
    skin.middle = template.middle
    skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 300px;')
    skin.root().xpath('//div[@id="middle"]')[0].set('class','midlle_computer')
    return skin.render()

def promotion(template, skin, request):
    if globals()['gChoices'] is None:
        d = fillChoices()
        d.addCallback(lambda some: promotion(template, skin, request))
        return d

    splitted = request.path.split('/')
    name = unicode(unquote_plus(splitted[-1]), 'utf-8')
    if len(name) == 0 or name=='promotion':
        name = 'ajax'
    d = couch.openDoc(name)
    d.addCallback(renderPromotion, template, skin)
    return d


def upgrade_set(template, skin, request):
    if globals()['gChoices'] is None:
        d = fillChoices()
        d.addCallback(lambda some: upgrade_set(template, skin, request))
        return d
    def render(self):
        skin.top = template.top
        skin.middle = template.middle
        return skin.render()

    d = couch.openView(designID,'models',include_docs=True,stale=False)
    d.addCallback(render)
    return d



class Model(object):

    def buildProcAndVideo(self):
        proc_video = {}
        for c in self.components:
            if c.cat_name == proc:
                proc_video['proc_code'] = c._id
                #zzzzzzz
                proc_video['proc_catalog'] = c.getCatalogsKey()
                proc_video['brand'] = c.brand
                proc_video['cores'] = c.cores
                proc_video['cache'] = c.cache
            elif c.cat_name == video:
                proc_video['video_code'] = c._id
                proc_video['video_catalog'] = c.getCatalogsKey()
        return proc_video


    def getComponentCount(self, component):
        retval = 1
        code = self.model_doc['items'][component.cat_name]
        if type(code) is list:
            retval = len(code)
        return retval


    def get(self, field, default=None):
        return self.model_doc.get(field, default)


    @property
    def author(self):
        return self.get('author','')

    @property
    def parent(self):
        return self.get('parent','')


    @property
    def modeldesc(self):
        return self.get('modeldesc', False)


    @property
    def processing(self):
        return self.get('processing', False)

    @property
    def comments(self):
        return [Comment(c) for c in self.get('comments', [])]

    @property
    def isPromo(self):
        return self.get('promo', False)

    @property
    def order(self):
        return self.get('order', 0)

    @property
    def _id(self):
        retval = self.get('_id', '')
        if self.isOrder:
            retval = retval.replace('order_','')
        return retval

    @property
    def checkRequired(self):
        return 'checkModel' in self.model_doc

    @property
    def checkPerformed(self):
        return self.model_doc.get('checkModel', False)

    @property
    def name(self):
        return self.get('name', False)

    @property
    def title(self):
        return self.get('title', False)

    @property
    def ourPrice(self):
        return self.get('our_price', False)

    def __iter__(self):
        for k,v in self.model_doc['items'].items():
            # fucken legacy
            if k == 'tablet_catalog':
                k = tablet
            yield k,v


    def getCode(self, cat_name):
        retval = None
        for k,v in self:
            if k==cat_name:
                retval = v
        return retval

    def nameForCode(self, code):
        retval = None
        for _name,_code in self:
            if type(_code) is list and code in _code:
                retval = _name
                break
            elif  code == _code:
                retval = _name
                break
        return retval

    def getComponents(self):
        return sorted(self.components, lambda c1,c2:parts[c1.cat_name]-parts[c2.cat_name])

    @property
    def installing(self):
        return self.get('installing', False)

    @property
    def building(self):
        return self.get('building', False)

    @property
    def dvd(self):
        return self.get('dvd', False)

    @property
    def date(self):
        return self.get('date')

    def isAuthor(self, user):
        is_author = self.get('author') == user._id
        is_merged = self.get('author') in user.get('merged_docs', [])
        return is_author or is_merged

    @property
    def motherCatalogs(self):
        return self.get('mother_catalogs')

    @property
    def procCatalogs(self):
        return self.get('proc_catalogs')

    def __init__(self, model_doc):
        self.model_doc = model_doc
        self.isOrder = False
        self.orderComponents = []
        if self.get('_id').startswith('order'):
            self.orderComponents = self.model_doc['components']
            self.model_doc = model_doc['model']
            self.isOrder = True
        self.components = []
        self.cat_prices = {}
        self.component_prices = {}
        self.total = 0
        self.case = None
        self.walkOnComponents()

    # TODO why do i need that??? grep for method name 
    def updateCatPrice(self, catalogs, required_catalogs, price):
        if catalogs == required_catalogs:
            self.cat_prices.update({self.aliasses_reverted[required_catalogs]:price})

    @property
    def original_prices(self):
        return self.get('original_prices', {})

    @classmethod
    def getCatalogsKey(cls, doc):        
        if 'catalogs' not in doc:
            return 'no'
        if type(doc['catalogs'][0]) is dict:
            cats = []
            for c in doc['catalogs']:
                cats.append(str(c['id']))
            return cats
        return doc['catalogs']


    @classmethod
    def makePrice(cls, doc):
        #orders! they prices are fixed
        if 'ourprice' in doc:
            return doc['ourprice']
        if doc['price'] == 0:
            return 0
        course = Course
        catalog = Model.getCatalogsKey(doc)
        if catalog == windows:
            course = 1
        our_price = float(doc['price'])*Margin*course
        # notes and tablets has notes as second element of catalogs
        # so first check for tableyt
        if catalog[-1] == tablet:
            our_price = doc['price']*Course+TABLET_MARGIN
            if our_price>10000:
                our_price+=400
            if our_price>20000:
                our_price+=400
        elif catalog[1] == notes:        
            our_price = doc['price']*Course+NOTE_MARGIN
        return int(round(our_price/100))*100


    @property
    def ours(self):
        return self.get('ours', False)


    # TODO! than replace mother or video
    # check slots! may be 2 video installed with sli or with crossfire!
    def replaceComponent(self, code):
        original_price = self.original_prices[code] \
            if code in self.original_prices else 130 #it is good price! about 4000 rubles
        if type(original_price) is dict and 'price' in original_price:
             original_price = original_price['price']
        # name = nameForCode(code,model)
        name = self.nameForCode(code)
        def sameCatalog(doc):
            retval = True
            if mother==name:
                retval = self.motherCatalogs == self.getCatalogsKey(doc)
            if proc==name:
                retval = self.procCatalogs == self.getCatalogsKey(doc)
            return retval
        choices = globals()['gChoices'][name]
        flatten = []
        if type(choices) is list:
            for el in choices:
                if el[0]:
                    for ch in el[1][1]['rows']:
                        if sameCatalog(ch['doc']):
                            flatten.append(ch['doc'])
        else:
            for ch in choices['rows']:
                if sameCatalog(ch['doc']):
                    flatten.append(ch['doc'])
        mock_component = noComponentFactory({},name)
        mock_component['price'] = original_price
        mock_component['_id'] = code
        flatten.append(mock_component)
        flatten = sorted(flatten,lambda x,y: int(x['price'] - y['price']))

        keys = [doc['_id'] for doc in flatten]
        _length = len(keys)
        ind = keys.index(code)
        _next = ind+1
        if _next == _length:
            _next = ind-1
        next_el = deepcopy(flatten[_next])
        if self.ours and code not in globals()['gWarning_sent']:
            globals()['gWarning_sent'].append(code)
            text = self.name + ' '+parts_names[name] + ': '+code
            send_email('admin@buildpc.ru',
                       u'В модели заменен компонент',
                       text,
                       sender=u'Компьютерный магазин <inbox@buildpc.ru>')
        return next_el

    @property
    def description(self):
        return self.get('description', '')

    def preparePdf(self):
        self.model_doc['full_items'] = []
        for c in self.components:
            doc = deepcopy(c.component_doc)
            doc['price'] = c.makePrice()
            self.model_doc['full_items'].append(doc)
        self.model_doc['const_prices'] = [DVD_PRICE, BUILD_PRICE, INSTALLING_PRICE]
        return self.model_doc

    @property
    def promoComponents(self):
        return [{u"_id": u"18225",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7383",u"name": u"Корпусы"},{u"id": u"10837",u"name": u"Exclusive Case"}],u"text": u"Корпус Silverstone SST-PS05B Precision Midi-Tower - black",u"price": 62},{u"_id": u"20156",u"text": u"Монитор LED Philips 226V3LSB 21.5'' DVI Black",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7384",u"name": u"Мониторы"},{u"id": u"13209",u"name": u"LCD 22-27\""}],u"price": 135   },{u"_id": u"17398",u"catalogs": [{u"id": u"7369",u"name": u"Программное обеспечение"},{u"id": u"14570",u"name": u"ПО Microsoft (цены в рублях)"},{u"id": u"14571",u"name": u"Microsoft Windows (цены в рублях)"}],u"text": u"ПО Microsoft Win 7 Home Basic 64-bit Rus CIS SP1",u"price": 2230},{u"_id": u"19992",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7388",u"name": u"Материнские платы"},{u"id": u"19238",u"name": u"SOCKET FM1"}],u"price": 68,u"text": u"Материнская плата GIGABYTE GA-A55M-S2V FM1 AMD A75 2DDR3 RAID mATX"},{u"_id": u"20017",u"text": u"Процессор AMD A4 X2 3300 2,5 ГГц Socket FM1 Box cashe 1Mb, TDP 65W (AWAD3300OJGXBOX)",u"price": 72,   u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7399",u"name": u"Процессоры"},{u"id": u"19257",u"name": u"SOCKET FM1"}]},{u"_id": u"19470",u"text": u"Видеокарта HD6450 XFX 1GB DDR3 DVI+VGA+HDMI BOX  HD-645X-ZNH2",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7396",u"name": u"Видеокарты"},{u"id": u"7613",u"name": u"RADEON PCI-E"}],   u"price": 52.59      },{u"_id": u"15318",u"text": u"Жесткий диск 1000GB WD GreenPower Sata2  64mb WD10EARS",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7406",u"name": u"Жесткие диски"},{u"id": u"7673",u"name": u"SATA II&III"}],u"price": 119},{u"_id": u"19575",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7394",u"name": u"Оперативная память"},{u"id": u"11576",u"name": u"DDRIII Лучшие цены"}],   u"text": u"ОЗУ DDR3 4096MB Crucial Rendition CL9 1333 PC3-10600",u"price": 19   },{u"_id": u"18692",u"catalogs": [{u"id": u"7365",u"name": u"Устройства ввода-вывода"},{u"id": u"7389",u"name": u"Акустические системы"},{u"id": u"7448",u"name": u"2.1 системы"}],u"text": u"Акустическая система Genius SW-M2.1 350, 11W black",u"price": 16.6},{u"_id": u"18932",u"text": u"Дисковод  Samsung SH-222AB/BEBE 22x SATA BLACK",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7392",u"name": u"Дисководы DVD RW, FDD"},{u"id": u"7538",u"name": u"DVD-RW"}],   u"price": 25},{u"_id": u"18244",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7416",u"name": u"Блоки питания"},{u"id": u"7464",u"name": u"500+W"}],u"reserved": 0,u"power": 500,u"text": u"Блок питания  500W Deluxe ATX SECC",u"price": 20,u"warranty_type": u"6 месяцев",u"flags": u"0",u"inCart": 0,u"stock1": 339,u"ordered": 0,u"id": "18238"}]

    def findComponent(self, cat_name):
        def lookFor():
            if self.isOrder:
                components = []
                for c in self.orderComponents:
                    if c['_id'].startswith('no'):
                        price = 0
                    else:
                        price = c['ourprice']*c.get('count',1)
                    components.append(cleanDoc(c, price, clean_text=False, clean_description=False))
                return lambda code: [c for c in components if c['_id'] == code][0]
            elif self.isPromo:
                components = []
                for c in self.promoComponents:
                    if c['_id'].startswith('no'):
                        price = 0
                    else:
                        price = c['price']
                    components.append(cleanDoc(c, price, clean_text=False, clean_description=False))
                return lambda code: [c for c in components if c['_id'] == code][0]
            else:
                return lambda code: globals()['gChoices_flatten'][code] if code in globals()['gChoices_flatten'] else None
        look_for = lookFor()
        # code = model['items'][name]
        code = self.getCode(cat_name)
        if type(code) is list:
            code = code[0]
        if code is None or code.startswith('no'):
            return noComponentFactory({},cat_name)
        retval = None
        # this try for those [0] in lambdas
        try:
            retval = look_for(code)
        except:
            pass
        if retval is None:
            retval = self.replaceComponent(code)
        ret = deepcopy(retval)
        ret['replaced'] = code != ret['_id']
        if ret['replaced']:
            ret['old_code'] = code
        return ret


    def getComponent(self, catalog):
        component = None        
        _type = type(catalog)
        for c in self.components:
            cat = c.getCatalogsKey()
            if _type is list:
                if cat == catalog:                    
                    component=c
                    break
            elif _type is str:
                if catalog in cat:
                    component=c
                    break
        return component


    def getComponentForIcon(self):
        if self.case is not None:
            return self.case
        retval = self.components[0]
        for c in self.components:
            if type(c) is VideoCard:
                retval = c
                break
            elif type(c) is Tablet:
                retval = c
                break
            elif type(c) is Note:
                retval = c
                break
        return retval
        
    def componentFactory(self, component_doc, cat_name):        
        catalog = self.getCatalogsKey(component_doc)
        component = Component(component_doc, cat_name)
        if catalog[-1] == tablet:
            component = Tablet(component_doc,cat_name)
        elif catalog[1] == notes:
            component = Note(component_doc,cat_name)
        else:
            if video in catalog:
                component = VideoCard(component_doc)
        return component



    def walkOnComponents(self):
        self.aliasses_reverted = {}
        for k,v in parts_aliases.items():
            self.aliasses_reverted.update({v:k})
        for cat_name,code in self:            
            count = 1
            if type(code) is list:
                count = len(code)
                code = code[0]
            component_doc = self.findComponent(cat_name)
            component = self.componentFactory(component_doc, cat_name)
            code = component_doc['_id']
            price = self.makePrice(component_doc)*count
            self.total += price
            self.updateCatPrice(cat_name,displ,price)
            self.updateCatPrice(cat_name,soft,price)
            self.updateCatPrice(cat_name,audio,price)
            self.updateCatPrice(cat_name,mouse,price)
            self.updateCatPrice(cat_name,kbrd,price)
            self.component_prices[code] = price
            self.components.append(component)
            if cat_name == case:
                self.case = component

        if self.installing:
            self.total += INSTALLING_PRICE
        if self.building:
            self.total += BUILD_PRICE
        if self.dvd:
            self.total += DVD_PRICE



class Component(object):

    def __init__(self, component_doc, cat_name=None):
        self.component_doc = component_doc
        self._cat_name = cat_name
        self._price = None


    def getComponentIcon(self, default = "/static/icon.png"):
        retval = default
        imgs = self.description.get('imgs',[])
        if len(imgs)>0:
                retval = ''.join(("/image/",self._id,"/",
                                  imgs[0],'.jpg'))
        if retval is not None and '/preview' in retval:
            splitted = retval.split('/preview')
            retval = splitted[0]+quote_plus('/preview'+splitted[1]).replace('.jpg', '')
        return retval

    @property
    def cat_name(self):
        if self._cat_name is None:
            self._cat_name = self.getCatalogsKey()[1]
        return self._cat_name

    def get(self, field, default=None):
        return self.component_doc.get(field, default)

    def __iter__(self):
        for k,v in self.component_doc.items():
            yield k,v

    @property
    def _id(self):
        return self.get('_id')
    @property
    def old_code(self):
        return self.get('old_code', False)

    @property
    def text(self):
        return self.get('text', '')

    @property
    def description(self):
        descr = self.get('description', {})
        if len(descr)==0:
            choices = globals()['gChoices_flatten']
            if self._id in choices:
                cached = choices[self._id]
                if 'description' in cached:
                    descr = cached['description']
        return descr


    def getCatalogsKey(self):
        return Model.getCatalogsKey(self.component_doc)

    @property
    def brand(self):
        return self.get('brand', '')
    @property
    def cores(self):
        return self.get('cores', '')
    @property
    def cache(self):
        return self.get('cache', '')

    def makePrice(self):
        if self._price is  None:
            self._price = Model.makePrice(self.component_doc)
        return self._price




def userFactory(name):
    user = couch.openDoc(name)

    results = {}

    def di(res, name):
        results[name] = res

    user.addCallback(di, 'user')

    def fail(fail):
        pass

    def installKey(doc, key):
        if doc is not None:
            doc['key'] = key
        return doc

    def getFields(some, name, orders=False):
        """ {'models':[3afs123, 3b456a], 'notebooks':['3afs456'... """
        defs = []
        if name in results['user']:
            for _id in results['user'][name]:
                uid = _id
                if orders:
                    uid = 'order_'+uid
                d = couch.openDoc(uid)
                d.addErrback(fail)
                defs.append(d)
        li = defer.DeferredList(defs)
        res_name = name
        if orders:
            res_name='orders_'+res_name
        li.addCallback(di, res_name)
        return li

    user.addCallback(getFields, 'models')
    user.addCallback(getFields, 'models', orders=True)

    user.addCallback(getFields, 'notebooks')
    user.addCallback(getFields, 'notebooks', orders=True)

    user.addCallback(getFields, 'promos')
    user.addCallback(getFields, 'promos', orders=True)

    user.addCallback(getFields, 'sets')
    user.addCallback(getFields, 'sets', orders=True)

    user.addCallback(lambda some: UserForCart(results))
    return user

# TODO! fix fucken cart!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# my cart is broken. it is fixed in fixCookies, but than put to it again - the total counter
# is broken again
class UserForCart(object):
    def __init__(self, results):
        """ if has orders - get orders instead appropriate models"""
        # TODO! refactor this shit!~!!!!!!!!!!!!!
        orders_models = [tu[1] for tu in results['orders_models'] if tu[1] is not None]
        self.models = orders_models
        orders_models_ids = [o['_id'].replace('order_','') for o in orders_models]
        for res,model in results['models']:
            if model is None:continue
            if res and model['_id'] not in orders_models_ids:
                self.models.append(model)


        orders_promos = [tu[1] for tu in results['orders_promos'] if tu[1] is not None]
        self.promos = orders_promos
        orders_promos_ids = [o['_id'].replace('order_','') for o in orders_promos]
        for res,model in results['promos']:
            if model is None:continue
            if res and model['_id'] not in orders_promos_ids:
                self.promos.append(model)



        orders_notebooks = [tu[1] for tu in results['orders_notebooks'] if tu[1] is not None]
        self.notebooks = orders_notebooks
        orders_notebooks_ids = [o['_id'] for o in orders_notebooks]
        for res,note in results['notebooks']:
            if note is None: continue
            if res and note['_id'] not in orders_notebooks_ids:
                self.notebooks.append(note)


        orders_sets = [tu[1] for tu in results['orders_sets'] if tu[1] is not None]
        self.sets = orders_sets
        orders_sets_ids = [o['_id'] for o in orders_sets]
        for res,_set in results['sets']:
            if _set is None:continue
            if res and _set['_id'] not in orders_sets_ids:
                self.sets.append(_set)
        self.user = results['user']


    def isValid(self, request):
        return  self.user['_id'] == request.getCookie('pc_user') and \
                self.user['pc_key'] == request.getCookie('pc_key')


    def modelsSort(self, m1,m2):
        if u''.join(m1['date'])>u''.join(m2['date']):
            return -1
        return 1


    def getUserModels(self):
        for m in sorted(self.models, self.modelsSort):
            yield Model(m)


    def getUserPromos(self):
        for m in sorted(self.promos, self.modelsSort):
            yield Model(m)



    def getUserNotebooks(self):
        for n in self.notebooks:
            yield Notebook(n)


    def getUserSets(self):
        for s in self.sets:
            yield Set(s)



    def get(self, field, default=None):
        return self.user.get(field, default)

    @property
    def _id(self):
        return self.get('_id')




class Comment(object):

    def __init__(self, comment_doc):
        self.comment_doc = comment_doc

    def get(self, field, default=None):
        return self.comment_doc.get(field, default)

    @property
    def date(self):
        return self.get('date',[])

    @property
    def body(self):
        return self.get('body','')


    @property
    def email(self):
        return self.get('email','')


    @property
    def author(self):
        return self.get('author','')


class VideoCard(Component):

    @property
    def youtube(self):
        return self.get('youtube', False)


    @property
    def rate(self):
        return int(self.get('rate', 4))

    @property
    def cores(self):
        return self.get('cores', '384')

    @property
    def year(self):
        return self.get('year', '01.2010')

    @property
    def power(self):
        return self.get('power', 200)


    @property
    def memory(self):
        return self.get('memory', '1024')

    @property
    def memory_ammo(self):
        return self.get('memory_ammo', '-')


    @property
    def vendor(self):
        return self.get('vendor', '-')

    @property
    def chip(self):
        return self.get('chip', self._id)

    @property
    def hid(self):
        """ hidden id"""
        return self.get('articul', self._id.replace('new_','_')).lstrip().rstrip()

    @property
    def marketParams(self):
        return self.get('marketParams', default='<table></table>')

    @property
    def marketComments(self):
        return self.get('marketComments')

    @property
    def marketReviews(self):
        return self.get('marketReviews')


    def has(self, field):
        return self.get(field,default='-1')!='-1'

    @property
    def url(self):
        return '/videocard/'+\
             quote_plus(self.get('articul','').replace('\t',''))



class Psu(Component):
    @property
    def power(self):
        return self.get('power',0)


class Note(Component):
    @property
    def url(self):
        return '/notebook'

class Notebook(Model):

    @property
    def name(self):
        return u'Ноутбук'    



class Set(Model):
    @property
    def name(self):
        return u'Компьютерные компоненты'


# TODO! common class for couch docs
class UserForCredit(object):

    class CreditData(object):
        def __init__(self, order_id, data, file_names, attachments,deleted_files, parent):
            self.order_id = order_id
            self.data = data
            self.file_names = file_names
            self.attachments = attachments
            self.deleted_files = deleted_files
            self.parent = parent



    def __init__(self, user_doc):
        self.user_doc = user_doc




    def get(self, field, default=None):
        return self.user_doc.get(field, default)

    def __iter__(self):
        for k,v in self.user_doc.items():
            yield k,v

    @property
    def _id(self):
        return self.get('_id')

    def get_credits(self):
        if not 'credits' in self.user_doc:
            self.user_doc['credits'] = {}
        return self.user_doc['credits']

    def set_credits(self, value):
        self.user_doc['credits'] = value

    _credits = property(get_credits, set_credits)

    def updateCredits(self, credit_data):
        # copy old attachments
        credit_data.data['attachments'] = {}
        for k,v in self._credits.get(credit_data.order_id, {}).get('attachments',{}).items():
            credit_data.data['attachments'][k] = v
        self._credits[credit_data.order_id] = credit_data.data

        # first - store uploaded files
        for k,v in credit_data.file_names.items():
            self._credits[credit_data.order_id]['attachments'][k] = v
        d = couch.addAttachments(self.user_doc, credit_data.attachments)
        # than if has parent copy all attachments from parent except deleted!!!!!!!!!
        if credit_data.parent is not None and self._credits.get(credit_data.parent, False):
            for k,v in self._credits[credit_data.parent].get('attachments',{}).items():
                if k not in credit_data.deleted_files:
                    self._credits[credit_data.order_id]['attachments'][k] = v
        d.addCallback(couch.saveDoc)
        return d

    def deleteAttachment(self, field, order_id, pc_key):
        if pc_key != self.user_doc['pc_key']:
            return "ok"
        attachments =  self._credits.get(order_id, {}).get('attachments',{})
        file_name = attachments.get(field, None)
        if file_name is not None:
            attachments.pop(field)
            need_delete_file = True
            for data in self._credits.values():
                if field in data.get('attachments',{}):
                    need_delete_file = False
                    break
            if need_delete_file:
                _attachments = self.user_doc.get('_attachments',{})
                if file_name in _attachments:
                    self.user_doc['_attachments'].pop(file_name)
            couch.saveDoc(self.user_doc)
        return "ok"

    def summForForm(self):
        pass

    idle_name = 'empty'

    def getStoredCredit(self, _name, pc_key):
        """ gets order name and return stored credit, if any, and the name of this credit,
            which will be the parent of new credit
        """
        credit = name = None
        if pc_key == self.user_doc['pc_key'] and len(self._credits)>0:
            if _name in self._credits:
                credit = self._credits[_name]
                name = _name
            elif self.idle_name in self._credits:
                credit = self._credits[self.idle_name]
                name = self.idle_name
            else:
                for k in self._credits:
                    break
                credit = self._credits[k]
                name = k
        return credit, name


class UserForSaving(object):
    def __init__(self, user_doc):
        self.user_doc = user_doc

    @classmethod
    def makeNewUser(cls, user_id=None):
        if user_id is None:
            user_id = base36.gen_id()
        pc_key = base36.gen_id()        
        if pc_key == user_id:
            pc_key = user_id+str(randint(0,10))
        return {'_id':user_id, 'pc_key':pc_key}

    def get(self, field, default=None):
        return self.user_doc.get(field, default)

    @property
    def pc_key(self):
        if self.get('pc_key',None) is None:
            self.user_doc['pc_key'] = base36.gen_id()
        return self.get('pc_key')

    @property
    def _id(self):
        return self.get('_id')


    def isValid(self, pc_key):
        return pc_key == self.pc_key

    def addModel(self, modelForSaving):
        placement = modelForSaving.placement
        if modelForSaving._id not in self.get(placement,[]):
            self.user_doc.setdefault(placement,[]).append(modelForSaving._id)

    def addDate(self):
        self.user_doc['date'] = str(date.today()).split('-')



    def save(self):
        return couch.saveDoc(self.user_doc)


class ModelForSaving(object):
    def __init__(self, model_doc, editing=False):
        self.model_doc = model_doc
        self.editing = editing

    @property
    def _id(self):
        return self.get('_id')


    def get(self, field, default=None):
        return self.model_doc.get(field, default)

    @property
    def processing(self):
        return self.get('processing',False)


    def addDate(self):
        self.model_doc['date'] = str(date.today()).split('-')


    def setId(self):
        self.model_doc['_id'] = base36.gen_id()
        return self

    def updateModel(self, new_model):
        for k,v in new_model.items():
            self.model_doc[k] = v

    def setOriginalPrices(self):
        self.model_doc['original_prices'] = {}
        choices = globals()['gChoices_flatten']
        for name,code in self.model_doc['items'].items():
            if type(code) is list:
                code = code[0]
            if code in choices:
                #fuck slava! here was no ['price']
                self.model_doc['original_prices'].update({code:choices[code]['price']})
            else:
                self.model_doc['original_prices'].update({code:0})


    def addAuthor(self, userForSaving):
        self.model_doc['author'] = userForSaving._id

    @property
    def promo(self):
        return self.get('promo', False)

    @property
    def placement(self):
        return 'promos' if self.promo else 'models'


    def save(self):
        return couch.saveDoc(self.model_doc)


class Tablet(Component):
    @property
    def url(self):
        url = '/tablet/'+self.get('vendor','')+'_'+self.get('model','')
        return url.replace(' ','_')

    @property
    def vendor(self):
        return self.get('vendor','')
    
    @property
    def model(self):
        return self.get('model','')

    @property
    def screen(self):
        return self.get('screen','')

    @property
    def memory(self):
        return self.get('memory','')


    @property
    def flash(self):
        return self.get('flash','')


    @property
    def os(self):
        return self.get('os','')

    @property
    def resolution(self):
        return self.get('resolution','')

    @property
    def rank(self):
        return int(self.get('rank','0'))

    @property
    def youtube(self):
        return self.component_doc.get('youtube',False)


def makeNotePrice(doc):
    our_price = doc['price']*Course+NOTE_MARGIN
    copy = deepcopy(doc)
    copy['price'] = int(round(our_price/100))*100
    return copy


class Router(Component):
    pass


class Sd(Component):
    pass

