# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from lxml import etree, html
from twisted.internet import defer
import simplejson
import re
from copy import deepcopy
from urllib import unquote_plus, quote_plus
from datetime import datetime,timedelta
from pc.mail import send_email
from twisted.web.resource import Resource
from pc.common import MIMETypeJSON, forceCond

BUILD_PRICE = 800
INSTALLING_PRICE=800
DVD_PRICE = 800
NOTE_MARGIN=1500

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
power = [components,"7416","7464"]



mother_to_proc_mapping= [(mother_1155,proc_1155),
                         (mother_1156,proc_1156),
                         (mother_1366,proc_1366),
                         (mother_775,proc_775),
                         (mother_am23,proc_am23),
                         (mother_fm1,proc_fm1)]




Margin=1.15
Course = 32.2

#refactor (just comment it and youl see
def cleanDoc(doc, price, clean_text=True, clean_description=True):
    new_doc = {}
    to_clean = ['id', '_attachments','flags','inCart',
                     'ordered','reserved','stock1', '_rev', 'warranty_type',
                'articul', 'rur_price','us_price','us_recommended_price', 'rur_recommended_price',
                'new_stock', 'new_link', 'new_catalogs']
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
         kbrd:120, mouse:130, audio:140}

parts_names = {proc:u'Процессор', ram:u'Память',
               video:u'Видеокарта', hdd:u'Жесткий диск', case:u'Корпус',
               sound:u'Звуковая карта',
               network:u'Сетевая карта',
               mother:u'Материнская плата',displ:u'Монитор',
               audio:u'Аудиосистема', kbrd:u'Клавиатура', mouse:u'Мышь',
               soft:u'ОС'}


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
    'case':case
    }

def noComponentFactory(_doc, name):
    no_name = 'no' + name
    no_doc = deepcopy(_doc)
    no_doc['_id'] = no_name
    no_doc['price'] = 0
    no_doc['text'] = parts_names[name] + u': нет'
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



def equipCases(result):
    exclusive_rows = power = power_index = None
    i=0
    for r in result:
        if r[1][0] == u"Эксклюзивные корпусы":
            exclusive_rows = r[1][1]['rows']
        elif r[1][0] == u"БП":
            power = r[1][1]
            power_index = i
        i+=1
    chipest_power = sorted([row['doc'] for row in power['rows']],lambda x,y:int(x['price']-y['price']))[0]
    for r in exclusive_rows:
        r['doc']['price'] += chipest_power['price']
        r['doc']['text'] = r['doc']['text'].replace(u'без БП', '')
    result.pop(power_index)
    return result




def fillChoices():
    # docs = [r['doc'] for r in result['rows'] if r['key'] is not None]
    _gChoices = globals()['gChoices']
    if _gChoices is not None:
        d = defer.Deferred()
        d.addCallback(lambda x: _gChoices)
        d.callback(None)
        return d
    defs = []
    defs.append(defer.DeferredList([
                # couch.openView(designID,
                #                                  'catalogs',
                #                                  include_docs=True, key=mother_1366, stale=False)
                #                   .addCallback(lambda res: ("LGA1366",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mother_1155, stale=False)
                                    .addCallback(lambda res: ("LGA1155",res)),
                                    # couch.openView(designID,
                                    #                'catalogs',
                                    #                include_docs=True, key=mother_1156, stale=False)
                                    # .addCallback(lambda res: ("LGA1166",res)),
                                    # couch.openView(designID,
                                    #                'catalogs',
                                    #                include_docs=True, key=mother_775, stale=False)
                                    # .addCallback(lambda res: ("LGA775",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mother_am23, stale=False)
                                    .addCallback(lambda res: ("AM2 3",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mother_fm1, stale=False)
                                    .addCallback(lambda res: ("FM1",res))
                                    ])
                .addCallback(lambda res: {mother:res}))


    defs.append(defer.DeferredList([couch.openView(designID,
                                                   "catalogs",
                                                   include_docs=True,key=proc_1155, stale=False)
                                    .addCallback(lambda res:('LGA1155',res)),
                                    # couch.openView(designID,
                                    #                'catalogs',
                                    #                include_docs=True,key=proc_1156, stale=False)
                                    #                .addCallback(lambda res:('LGA1156',res)),
                                    # couch.openView(designID,
                                    #              'catalogs',
                                    #              include_docs=True,key=proc_1366, stale=False)
                                    #              .addCallback(lambda res:('LGA1366',res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True,key=proc_am23, stale=False)
                                    .addCallback(lambda res:('AM2 3',res)),
                                    # couch.openView(designID,
                                    #                'catalogs',
                                    #                include_docs=True,key=proc_775, stale=False)
                                    #                .addCallback(lambda res:('LGA755',res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=proc_fm1, stale=False)
                                    .addCallback(lambda res: ("FM1",res))
                                    ])

                .addCallback(lambda res: {proc:res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=geforce, stale=False)
                                    .addCallback(lambda res: (u"GeForce",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=radeon, stale=False)
                                    .addCallback(lambda res: (u"Radeon",res))])
                .addCallback(lambda res: {video:res}))

    defs.append(couch.openView(designID,
                               'catalogs',include_docs=True, key=ddr3, stale=False)
                .addCallback(lambda res: {ram:res}))
    defs.append(couch.openView(designID,
                               'catalogs',include_docs=True, key=satas, stale=False)
                .addCallback(lambda res: {hdd:res}))
    defs.append(couch.openView(designID,
                               'catalogs',include_docs=True, key=windows, stale=False)
                .addCallback(lambda res: {soft:res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=case_400_650, stale=False)
                                    .addCallback(lambda res: (u"Корпусы 400-650 Вт",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=power, stale=False)
                                    .addCallback(lambda res: (u"БП",res)),
                                   couch.openView(designID,
                                                  'catalogs',include_docs=True, key=case_exclusive, stale=False)
                                    .addCallback(lambda res: (u"Эксклюзивные корпусы",res))])
                .addCallback(equipCases)
                .addCallback(lambda res: {case:res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=displ_19_20, stale=False)
                                    .addCallback(lambda res: (u"Мониторы 19-20 дюймов",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=displ_22_26, stale=False)
                                    .addCallback(lambda res: (u"Мониторы 22-26 дюймов",res))])
                .addCallback(lambda res: {displ:res}))


    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrd_a4, stale=False)
                                    .addCallback(lambda res: (u"Клавиатуры A4Tech",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrd_acme, stale=False)
                                    .addCallback(lambda res: (u"Клавиатуры Acme",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrd_chikony, stale=False)
                                    .addCallback(lambda res: (u"Клавиатуры Chikony",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrd_game, stale=False)
                                    .addCallback(lambda res: (u"Игровые Клавиатуры",res)),])
                .addCallback(lambda res: {kbrd:res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouse_a4, stale=False)
                                    .addCallback(lambda res: (u"Мыши A4Tech",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouse_game, stale=False)
                                    .addCallback(lambda res: (u"Игровые Мыши",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouse_acme, stale=False)
                                    .addCallback(lambda res: (u"Мыши Acme",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouse_genius, stale=False)
                                    .addCallback(lambda res: (u"Мыши Genius",res))])
                .addCallback(lambda res: {mouse:res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=audio_20, stale=False)
                                    .addCallback(lambda res: (u"Аудио системы 2.0",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=audio_21, stale=False)
                                    .addCallback(lambda res: (u"Аудио системы 2.1",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=audio_51, stale=False)
                                    .addCallback(lambda res: (u"Аудио системы 5.1",res))])
                .addCallback(lambda res: {audio:res}))
    def makeDict(res):
        new_res = {}
        for el in res:
            if el[0]:
                new_res.update(el[1])
        globals()['gChoices'] = new_res
        flatChoices(new_res)
        return globals()['gChoices']
    #TODO - this callback to the higher level
    return defer.DeferredList(defs).addCallback(makeDict).addCallback(fillNew)

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


def getNoteBookName(doc):

    if 'nname' in doc:
        return doc['nname']

    found = re.findall('[sSuU]+([a-zA-Z0-9 ]+)[ ][0-9\,\.0-9"]+[ ]',doc['text'])
    _text = None
    if len(found)>0:
        _text = found[0].strip()
        # doc['nname'] =_text
        # couch.saveDoc(doc)
    else:
        _text = doc['text'][0:doc['text'].index('"')]
        _text = _text.replace(u'Ноутбук ASUS','').replace(u'Ноутбук Asus','')
    return _text


def getNoteDispl(doc):
    if 'ndispl' in doc:
        return doc['ndispl']
    retval = ''
    found =re.findall('[sSuU]+[a-zA-Z0-9 ]+[ ]([0-9\,\.0-9"]+)[ ]',doc['text'])
    if len(found)>0:
        retval = found[0]
        # doc['ndispl'] =retval
        # couch.saveDoc(doc)
    return retval

def getNotePerformance(doc):
    if 'nperformance' in doc:
        return doc['nperformance']
    retval = ""
    found = re.findall('[0-9\,\.0-9"]+[ FHD, ]+([^/]*[/]+[^/]*)',doc['text'])
    if len(found)>0:
        retval = found[0]
        # doc['nperformance'] =retval
        # couch.saveDoc(doc)
    return retval


def makeNotePrice(doc):
    our_price = doc['price']*Course+NOTE_MARGIN
    return int(round(our_price/10))*10


@forceCond(noChoicesYet, fillChoices)
def notebooks(template, skin, request):
    def render(result):
        json_notebooks= {}
        for r in result['rows']:

            r['doc']['price'] = makeNotePrice(r['doc'])

            note_div = deepcopy(template.root().find('notebook').find('div'))
            note_div.set('class',r['doc']['_id']+' note')


            link = note_div.xpath("//div[@class='nname']")[0].find('a')
            name = getNoteBookName(r['doc'])
            link.text = name
            if 'ourdescription' in r['doc']:
                link.set('href','/notebook/'+name)
            else:
                link.set('name',name)

            for d in template.middle.xpath("//div[@class='notebook_column']"):
                clone = deepcopy(note_div)
                sort_div = clone.xpath("//div[@class='nprice']")[0]
                if d.get('id') == "s_price":
                    sort_div.text = unicode(r['doc']['price'])+u' р.'
                if d.get('id') == "s_size":
                    sort_div.text = getNoteDispl(r['doc'])
                if d.get('id') == "s_size":
                    sort_div.text = getNoteDispl(r['doc'])
                if d.get('id') == "s_performance":
                    sort_div.text = getNotePerformance(r['doc'])
                d.append(clone)

            for token in ['id', 'flags','inCart',
                          'ordered','reserved','stock1', '_rev', 'warranty_type']:
                r['doc'].pop(token)
            r['doc']['catalogs'] = Model.getCatalogsKey(r['doc'])
            #TODO save all this shit found from re
            json_notebooks.update({r['doc']['_id']:r['doc']})

        template.middle.find('script').text = 'var notebooks=' + simplejson.dumps(json_notebooks)
        title = skin.root().xpath('//title')[0]
        title.text = u'Ноутбуки Asus'
        skin.top = template.top
        skin.middle = template.middle
        return skin.render()
    asus_12 = ["7362","7404","7586"]
    asus_14 = ["7362","7404","7495"]
    asus_15 = ["7362","7404","7468"]
    asus_17 = ["7362","7404","7704"]
    d = couch.openView(designID,'catalogs',include_docs=True,stale=False,
                       keys = [asus_12,asus_14,asus_15,asus_17])
    d.addCallback(render)
    return d

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
        return self.get('checkModel', False)

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
        self.walkOnComponents()

    def updateCatPrice(self, catalogs, required_catalogs, price):
        if catalogs == required_catalogs:
            self.cat_prices.update({self.aliasses_reverted[required_catalogs]:price})


    def getComponentPrice(self, component_doc):
        return self.component_prices[component_doc._id]


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
    def getComponentIcon(cls, component_doc, default = "/static/icon.png"):
        retval = default
        if 'description' in component_doc and'imgs' in component_doc['description']:
            imgs = component_doc['description']['imgs']
            if len(imgs)>0:
                retval = ''.join(("/image/",component_doc['_id'],"/",
                                  imgs[0],'.jpg'))
        if retval is not None and '/preview' in retval:
            splitted = retval.split('/preview')
            retval = splitted[0]+quote_plus('/preview'+splitted[1]).replace('.jpg', '')
        return retval
            

    @classmethod
    def makePrice(cls, doc):
        #orders! they prices are fixed
        if 'ourprice' in doc:
            return doc['ourprice']
        if doc['price'] == 0:
            return 0
        course = Course
        if Model.getCatalogsKey(doc) == windows:
            course = 1
        our_price = float(doc['price'])*Margin*course
        return int(round(our_price/10))*10
    

    @property
    def ours(self):
        return self.get('ours', False)


    # TODO! than replace mother or video
    # check slots! may be 2 video installed with sli or with crossfire!
    def replaceComponent(self, code):
        original_price = self.original_prices[code] \
            if code in self.original_prices else 10
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
        for k,v in self:
            if type(v) is list:
                v = v[0]
            if v is None: continue
            if v.startswith('no'):continue
            component = deepcopy(self.findComponent(k))
            component['price'] = Model.makePrice(component)
            self.model_doc['full_items'].append(component)
        self.model_doc['const_prices'] = [DVD_PRICE, BUILD_PRICE, INSTALLING_PRICE]
        return self.model_doc

    @property
    def promoComponents(self):
        return [{u"_id": u"18225",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7383",u"name": u"Корпусы"},{u"id": u"10837",u"name": u"Exclusive Case"}],u"text": u"Корпус Silverstone SST-PS05B Precision Midi-Tower - black",u"price": 62},{u"_id": u"20156",u"text": u"Монитор LED Philips 226V3LSB 21.5'' DVI Black",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7384",u"name": u"Мониторы"},{u"id": u"13209",u"name": u"LCD 22-27\""}],u"price": 135   },{u"_id": u"17398",u"catalogs": [{u"id": u"7369",u"name": u"Программное обеспечение"},{u"id": u"14570",u"name": u"ПО Microsoft (цены в рублях)"},{u"id": u"14571",u"name": u"Microsoft Windows (цены в рублях)"}],u"text": u"ПО Microsoft Win 7 Home Basic 64-bit Rus CIS SP1",u"price": 2230},{u"_id": u"19992",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7388",u"name": u"Материнские платы"},{u"id": u"19238",u"name": u"SOCKET FM1"}],u"price": 68,u"text": u"Материнская плата GIGABYTE GA-A55M-S2V FM1 AMD A75 2DDR3 RAID mATX"},{u"_id": u"20017",u"text": u"Процессор AMD A4 X2 3300 2,5 ГГц Socket FM1 Box cashe 1Mb, TDP 65W (AWAD3300OJGXBOX)",u"price": 72,   u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7399",u"name": u"Процессоры"},{u"id": u"19257",u"name": u"SOCKET FM1"}]},{u"_id": u"19470",u"text": u"Видеокарта HD6450 XFX 1GB DDR3 DVI+VGA+HDMI BOX  HD-645X-ZNH2",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7396",u"name": u"Видеокарты"},{u"id": u"7613",u"name": u"RADEON PCI-E"}],   u"price": 52.59      },{u"_id": u"15318",u"text": u"Жесткий диск 1000GB WD GreenPower Sata2  64mb WD10EARS",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7406",u"name": u"Жесткие диски"},{u"id": u"7673",u"name": u"SATA II&III"}],u"price": 119},{u"_id": u"19575",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7394",u"name": u"Оперативная память"},{u"id": u"11576",u"name": u"DDRIII Лучшие цены"}],   u"text": u"ОЗУ DDR3 4096MB Crucial Rendition CL9 1333 PC3-10600",u"price": 19   },{u"_id": u"18692",u"catalogs": [{u"id": u"7365",u"name": u"Устройства ввода-вывода"},{u"id": u"7389",u"name": u"Акустические системы"},{u"id": u"7448",u"name": u"2.1 системы"}],u"text": u"Акустическая система Genius SW-M2.1 350, 11W black",u"price": 16.6},{u"_id": u"18932",u"text": u"Дисковод  Samsung SH-222AB/BEBE 22x SATA BLACK",u"catalogs": [{u"id": u"7363",u"name": u"Компьютерные компоненты"},{u"id": u"7392",u"name": u"Дисководы DVD RW, FDD"},{u"id": u"7538",u"name": u"DVD-RW"}],   u"price": 25}]

    def findComponent(self, cat_name):
        def lookFor():
            if self.isOrder:
                components = []
                for c in self.orderComponents:
                    if c['_id'].startswith('no'):
                        price = 0
                    else:
                        price = c['ourprice']*c['count']
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

        retval = look_for(code)
        if retval is None:
            retval = self.replaceComponent(code)
        ret = deepcopy(retval)
        ret['replaced'] = code != ret['_id']
        if ret['replaced']:
            ret['old_code'] = code
        return ret


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
            code = component_doc['_id']
            price = Model.makePrice(component_doc)*count
            self.total += price
            self.updateCatPrice(cat_name,displ,price)
            self.updateCatPrice(cat_name,soft,price)
            self.updateCatPrice(cat_name,audio,price)
            self.updateCatPrice(cat_name,mouse,price)
            self.updateCatPrice(cat_name,kbrd,price)
            self.component_prices[code] = price
            self.components.append(Component(component_doc, cat_name))
            if cat_name == case:
                self.case = Component(component_doc, case)

        if self.installing:
            self.total += INSTALLING_PRICE
        if self.building:
            self.total += BUILD_PRICE
        if self.dvd:
            self.total += DVD_PRICE



class Component(object):

    def __init__(self, component_doc, cat_name=None):
        self.component_doc = component_doc
        # ???
        self._cat_name = cat_name
    
    @property
    def cat_name(self):
        if self._cat_name is not None:
            return self._cat_name
        else:
            return self.getCatalogsKey()[1]
                

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
        return self.get('text', False)

    @property
    def description(self):
        return self.get('description', False)


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
        return Model.makePrice(self.component_doc)




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

    def getFields(some, name, orders=False, keys=False):
        """ {'models':[3afs123, 3b456a], 'notebooks':{'3afs456':171515}} """
        defs = []
        if name in results['user']:
            for _id in results['user'][name]:
                uid = _id
                if keys:
                    uid = results['user'][name][uid]
                if orders:
                    uid = 'order_'+uid
                d = couch.openDoc(uid)
                d.addErrback(fail)
                if keys:
                    d.addCallback(installKey, _id)
                defs.append(d)
        li = defer.DeferredList(defs)
        res_name = name
        if orders:
            res_name='orders_'+res_name
        li.addCallback(di, res_name)
        return li

    user.addCallback(getFields, 'models')
    user.addCallback(getFields, 'notebooks', keys=True)
    user.addCallback(getFields, 'models', orders=True)
    user.addCallback(getFields, 'notebooks', orders=True, keys = True)
    user.addCallback(lambda some: User(results))
    return user


class User(object):
    def __init__(self, results):
        """ if has orders - get orders instead appropriate models"""
        orders_models = [tu[1] for tu in results['orders_models'] if tu[1] is not None]
        self.models = orders_models
        orders_models_ids = [o['_id'].replace('order_','') for o in orders_models]
        for res,model in results['models']:
            if res and model['_id'] not in orders_models_ids:
                self.models.append(model)

        orders_notebooks = [tu[1] for tu in results['orders_notebooks'] if tu[1] is not None]
        self.notebooks = orders_notebooks
        orders_notebooks_ids = [o['_id'] for o in orders_notebooks]
        for res,note in results['notebooks']:
            if res and note['_id'] not in orders_notebooks_ids:
                self.notebooks.append(note)
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

    def getUserNotebooks(self):
        for n in self.notebooks:
            yield Notebook(n, None)


    def get(self, field, default=None):
        return self.user.get(field, default)

    @property
    def _id(self):
        return self.get('_id')




class Notebook(Component):

    @property
    def key(self):
        return self.get('key')


    def makePrice(self):
        our_price = self.component_doc['price']*Course+NOTE_MARGIN
        return int(round(our_price/10))*10


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


    def goodPrice(self):        
        return self.makePrice()>=4000

    @property
    def cores(self):
        return self.get('cores', '-')

    @property
    def year(self):
        return self.get('year', '-')

    @property
    def power(self):
        return self.get('power', '-')


    @property
    def memory(self):
        return self.get('memory', '-')

    @property
    def memory_ammo(self):
        return self.get('memory_ammo', '-')

    def getComponentIcon(self, default = "/static/icon.png"):
        return Model.getComponentIcon(self.component_doc, default = default)

    @property
    def vendor(self):
        return self.get('vendor', '-')

    @property
    def chip(self):
        return self.get('chip', self._id)

    @property
    def hid(self):
        """ hidden id"""
        return self._id.replace('new_','_')
