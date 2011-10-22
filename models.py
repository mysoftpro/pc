# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from lxml import etree
from twisted.internet import defer
import simplejson
import re
from copy import deepcopy
from urllib import unquote_plus
from datetime import datetime,timedelta
from pc.mail import send_email
from random import randint

BUILD_PRICE = 800
INSTALLING_PRICE=800
DVD_PRICE = 800

gWarning_sent = []

components = "7363"
perifery = "7365"


proc = "7399"
mother = "7388"

mother_1155 = [components, mother,"17961"]
mother_1156 = [components,mother,"12854"]
mother_1366 =[components,mother,"18029"]
mother_775 = [components,mother,"7449"]
mother_am23 = [components,mother,"7699"]
mother_fm1 = [components,mother,"19238"]

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

proc_1155 = [components, proc, "18027"]
proc_1156 = [components,proc,"18028"]
proc_1366 = [components,proc,"9422"]
proc_775 = [components,proc,"7451"]
proc_am23 = [components,proc,"7700"]
proc_fm1 =  [components,proc,"19257"]

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


def walkOnChoices(name = None, _filter=None):
    choices = None
    if name is not None:
        choices =globals()['gChoices'][name]
    else:
        choices = (v for k,v in globals()['gChoices'].items())
    if _filter is None:
        _filter = lambda x: True

    if type(choices) is dict:
        for ch in choices['rows']:
            if _filter(ch['doc']):
                yield ch['doc']
    else:
        for el in choices:
            if el[0]:
                for ch in el[1][1]['rows']:
                    if _filter(ch['doc']):
                        yield ch['doc']



def getCatalogsKey(doc):
    if type(doc['catalogs'][0]) is dict:
        cats = []
        for c in doc['catalogs']:
            cats.append(str(c['id']))
        return cats
    return doc['catalogs']


def getModelComponents(model):
    for k,v in model['items'].items():
        if type(v) is list:
            for el in v:
                yield el
        else:
            yield v


def nameForCode(code,model):
    retval = None
    for _name,_code in model['items'].items():
        if type(_code) is list and code in _code:
            retval = _name
            break
        elif  code == _code:
            retval = _name
            break
    return retval



Margin=1.2
Course = 30.9

def makePrice(doc):
    if doc['price'] == 0:
        return 0
    course = Course
    if getCatalogsKey(doc) == windows:
        course = 1
    our_price = float(doc['price'])*Margin*course
    return int(round(our_price/10))*10


def cleanDoc(doc, price):
    new_doc = {}
    for token in doc:
        if token in ['id', 'text', '_attachments','description','flags','inCart',
                     'ordered','reserved','stock1', '_rev', 'warranty_type']:
            continue
        if token == 'catalogs':
            new_doc.update({token:getCatalogsKey(doc)})
        else:
            new_doc.update({token:doc[token]})
    new_doc['price'] = price
    return new_doc

imgs = ['static/comp_icon_1.png',
        'static/comp_icon_2.png',
        'static/comp_icon_3.png',
        'static/comp_icon_4.png'
        ]



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

# TODO! than replace mother or video
# check slots! may be 2 video installed with sli or with crossfire!
def replaceComponent(code,model):
    original_price = model['original_prices'][code] if code in ['original_prices'] else 10
    name = nameForCode(code,model)
    def sameCatalog(doc):
        retval = True
        if mother==name:
            retval = model['mother_catalogs'] == getCatalogsKey(doc)
        if proc==name:
            retval = model['proc_catalogs'] == getCatalogsKey(doc)
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
    if 'ours' in model and code not in globals()['gWarning_sent']:
        globals()['gWarning_sent'].append(code)
        text = model['name'] + ' '+parts_names[name] + ': '+code
        send_email('admin@buildpc.ru',
                   u'В модели заменен компонент',
                   text,
                   sender=u'Компьютерный магазин <inbox@buildpc.ru>')
    return next_el

no_component_added = False

def renderComputer(model, template, skin):
    _name = ''
    _uuid = ''
    author = ''
    parent = ''
    h2 =template.top.find('div').find('h2')
    # only original models have length
    if 'name' in model:
        _name= model['name']
    else:
        _name = model['_id']
        _uuid = model.pop('_id')
        author = model.pop('author')
        if 'parent' in model:
            parent = model.pop('parent')

    h2.text = _name

    if 'description' in model:
        # try:
            d = template.top.find('div').find('div')
            d.text = ''
            d.append(etree.fromstring(model['description']))
        # except:
        #     pass
    original_viewlet = template.root().find('componentviewlet')
    choices = globals()['gChoices']

    model_json = {}
    total = 0
    components_json = {}
    viewlets = []
    counted = {}

    def makeOption(row, price):
        # try:
            option = etree.Element('option')
            if 'font' in row['doc']['text']:
                row['doc']['text'] = re.sub('<font.*</font>', '',row['doc']['text'])
                row['doc'].update({'featured':True})
            option.text = row['doc']['text']

            option.text +=u' ' + unicode(price) + u' р'

            option.set('value',row['id'])
            return option
        # except:
        #     print row
    def appendOptions(options, container):
        for o in sorted(options, lambda x,y: x[1]-y[1]):
            container.append(o[0])


    def noComponent(name, component_doc, rows):
        #hack!
        component_doc['catalogs'] = getCatalogsKey(rows[0]['doc'])

        if globals()['no_component_added']:return
        if name not in [mouse,kbrd,displ,soft,audio, network,video]: return
        no_doc = noComponentFactory(component_doc, name)
        rows.insert(0,{'id':no_doc['_id'], 'key':no_doc['_id'],'doc':no_doc})

    def addComponent(_options, _row, current_id):
        _price= makePrice(_row['doc'])
        _option = makeOption(_row, _price)
        _options.append((_option, _price))
        if _row['id'] == current_id:
            _option.set('selected','selected')
        _cleaned_doc = cleanDoc(_row['doc'], _price)
        _id = _cleaned_doc['_id']
        if _id in counted:
            _cleaned_doc.update({'count':counted[_id]})
        components_json.update({_id:_cleaned_doc})


    def fillViewlet(_doc):
        tr = viewlet.find("tr")
        tr.set('id',name)
        body = viewlet.xpath("//td[@class='body']")[0]
        body.set('id',_doc['_id'])
        body.text = re.sub('<font.*</font>', '',_doc['text'])

        descr = etree.Element('div')
        descr.set('class','description')
        descr.text = ''

        manu = etree.Element('div')
        manu.set('class','manu')
        manu.text = ''

        our = etree.Element('div')
        our.set('class','our')
        our.text = u'нет рекоммендаций'

        clear = etree.Element('div')
        clear.set('style','clear:both;')
        clear.text = ''
        descr.append(manu);
        descr.append(our)
        descr.append(clear)
        return descr


    for name,code in model['items'].items():
        component_doc = None
        count = 1
        if code is None:
            component_doc = noComponentFactory({}, name)
        else:

            if type(code) is list:
                count = len(code)
                code = code[0]
                counted.update({code:count})

            component_doc = findComponent(model,name)

        if _uuid == '' and 'replaced' in component_doc:
            # no need 'replaced' alert' in original models
            component_doc.pop('replaced')

        viewlet = deepcopy(original_viewlet)
        descr = fillViewlet(component_doc)

        price = makePrice(component_doc)

        total += price

        cleaned_doc = cleanDoc(component_doc, price)
        cleaned_doc['count'] = count
        model_json.update({cleaned_doc['_id']:cleaned_doc})
        viewlet.xpath('//td[@class="component_price"]')[0].text = unicode(price*count) + u' р'

        ch = choices[name]
        options = []
        if type(ch) is list:
            noComponent(name, cleaned_doc, ch[0][1][1]['rows'])
            for el in ch:
                if el[0]:
                    option_group = etree.Element('optgroup')
                    option_group.set('label', el[1][0])
                    _options = []
                    for r in el[1][1]['rows']:
                        addComponent(_options, r, cleaned_doc['_id'])
                    appendOptions(_options, option_group)
                    options.append((option_group, 0))
        else:
            noComponent(name, cleaned_doc, ch['rows'])
            for row in ch['rows']:
                addComponent(options, row, cleaned_doc['_id'])

        select = viewlet.xpath("//td[@class='component_select']")[0].find('select')
        appendOptions(options, select)
        viewlets.append((parts[name],viewlet,descr))


    components_container = template.middle.xpath('//table[@id="components"]')[0]
    description_container = template.middle.xpath('//div[@id="descriptions"]')[0]

    globals()['no_component_added'] = True

    for viewlet in sorted(viewlets, lambda x,y: x[0]-y[0]):
        components_container.append(viewlet[1].find('tr'))
        description_container.append(viewlet[2])
    processing = False
    if 'processing' in model and model['processing']:
        processing = True
    template.middle.find('script').text = u''.join(('var model=',simplejson.dumps(model_json),
                                                    ';var processing=',simplejson.dumps(processing),
                                                    ';var uuid=',simplejson.dumps(_uuid),
                                                    ';var author=',simplejson.dumps(author),
                                                    ';var parent=',simplejson.dumps(parent),
                                                    ';var total=',unicode(total),
                                                    ';var choices=',simplejson.dumps(components_json),
                                                    ';var parts_names=',simplejson.dumps(parts_names),
                                                    ';var mother_to_proc_mapping=',
                                                    simplejson.dumps(mother_to_proc_mapping),
                                                    ';var proc_to_mother_mapping=',
                                                    simplejson.dumps([(el[1],el[0]) for el in mother_to_proc_mapping]),
                                                    ';var installprice=',str(INSTALLING_PRICE),
                                                    ';var buildprice=',str(BUILD_PRICE),
                                                    ';var dvdprice=',str(DVD_PRICE),

                                                    ';var idvd=',simplejson.dumps(model['dvd']),
                                                    ';var ibuilding=',simplejson.dumps(model['building']),
                                                    ';var iinstalling=',simplejson.dumps(model['installing']),
                                                    ';var Course=',str(Course),
                                                    ';var parts=',simplejson.dumps(parts_aliases)
                                                    ))

    skin.top = template.top
    skin.middle = template.middle
    skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 280px;')
    skin.root().xpath('//div[@id="middle"]')[0].set('class','midlle_computer')
    return skin.render()


from twisted.python import log
import sys

def pr(some):
    log.startLogging(sys.stdout)
    log.msg(some)
    return some



gChoices = None
gChoices_flatten = {}

def cleanFlattenChoice(doc):
    def _pop(name):
        if 'descriptions' in doc and name in doc['descriptions']:
            doc['descriptions'].pop(name)
    _pop('img')
    _pop('name')
    _pop('comments')

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
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mother_1156, stale=False)
                                    .addCallback(lambda res: ("LGA1166",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mother_775, stale=False)
                                    .addCallback(lambda res: ("LGA775",res)),
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
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True,key=proc_1156, stale=False)
                                                   .addCallback(lambda res:('LGA1156',res)),
                                    # couch.openView(designID,
                                    #              'catalogs',
                                    #              include_docs=True,key=proc_1366, stale=False)
                                    #              .addCallback(lambda res:('LGA1366',res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True,key=proc_am23, stale=False)
                                    .addCallback(lambda res:('AM2 3',res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True,key=proc_775, stale=False)
                                                   .addCallback(lambda res:('LGA7755',res)),
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
    return defer.DeferredList(defs).addCallback(makeDict)



def computer(template, skin, request):
    if globals()['gChoices'] is None:
        d = fillChoices()
        d.addCallback(lambda some: computer(template, skin, request))
        return d

    splitted = request.path.split('/')
    name = unicode(unquote_plus(splitted[-1]), 'utf-8')
    # hack! just show em ping!
    if len(name) == 0:
        name = 'ping'
    d = couch.openDoc(name)
    d.addCallback(renderComputer, template, skin)
    # d.addErrback(lambda x: couch.openDoc('cell').addCallback(renderComputer, template, skin))
    return d

def computers(template,skin,request):
    if globals()['gChoices'] is None:
        d = fillChoices()
        d.addCallback(lambda some: computers(template, skin, request))
        return d

    splitted = request.path.split('/')
    name = unicode(unquote_plus(splitted[-1]), 'utf-8')
    # cart is only /cart/12345. for /cart and for /computer - all models are shown
    this_is_cart = len(name) > 0 and name != 'computer' and name != 'cart'
    def render(result):
        models = [row['doc'] for row in result['rows'] if row['doc'] is not None]
        if not this_is_cart:
            models = sorted(models,lambda x,y: x['order']-y['order'])
        else:
            def sort(m1,m2):
                if u''.join(m1['date'])>u''.join(m2['date']):
                    return 1
                return -1
            models = sorted(models,sort)
        tree = template.root()
        container = template.middle.xpath('//div[@id="models"]')[0]

        json_prices = {}
        # TODO! make model view as for ComponentForModelsPage!!!!!!!!
        for m in models:
            model_snippet = tree.find('model')
            divs = deepcopy(model_snippet.findall('div'))
            model_div = divs[0]
            if 'processing' in m and m['processing']:
                header = model_div.find('h2')
                header.set('class', header.get('class')+ ' processing')
            a = model_div.find('.//a')
            a.set('href','/computer/%s' % m['_id'])
            if 'name' in m:
                a.text=m['name']
            else:
                a.text = m['_id']
            price_span = model_div.find('.//span')
            price_span.set('id',m['_id'])

            _components = buildPrices(m, json_prices, price_span)
            # TODO, move this logic to model view!!!!!!
            case_found = [c for c in _components if c.cat_name == case]
            if len(case_found) >0:
                icon = deepcopy(tree.find('model_icon').find('a'))
                icon.set('href','/computer/'+m['_id'])
                icon.find('img').set('src',case_found[0].getIconUrl())
                model_div.insert(0,icon)

            container.append(model_div)

            description_div = divs[1]

            ul = etree.Element('ul')
            ul.set('class','description')
            for cfm in _components:
                ul.append(cfm.render())
            description_div.append(ul)

            h3 = description_div.find('h3')
            if not this_is_cart:
                h3.text = m['title']
                description_div.append(etree.fromstring(m['description']))
                ul.set('style','display:none')
            else:
                h3.text = u'Пользовательская конфигурация'
                description_div.set('class','cart_description')
            container.append(description_div)

        _prices = 'undefined'
        if this_is_cart>0:
            cart = deepcopy(template.root().find('top_cart'))
            cart.xpath('//input[@id="cartlink"]')[0].set('value',"http://buildpc.ru/computer/"+name)
            cart_divs = cart.findall('div')
            for d in cart_divs:
                template.top.append(d)
        else:
            _prices =simplejson.dumps(json_prices) + ';'
            header = deepcopy(template.root().find('top_models'))
            header_divs = header.findall('div')
            for d in header_divs:
                template.top.append(d)
        template.middle.find('script').text = 'var prices=' + _prices;
        skin.top = template.top
        skin.middle = template.middle
        return skin.render()

    # RENDER MODELS HERE!!!
    if not this_is_cart:
        d = couch.openView(designID,'models',include_docs=True,stale=False)
        d.addCallback(render)
    # RENDER cart here!!!!
    else:
        d = couch.openDoc(name)
        d.addCallback(lambda doc:couch.listDoc(keys=doc['models'], include_docs=True))
        d.addCallback(render)
    return d



def findComponent(model, name):
    """ ??? i have a flat choices now! why do i need that?"""
    code = model['items'][name]
    if type(code) is list:
        code = code[0]
    if code is None or code.startswith('no'):
        return noComponentFactory({},name)
    replaced = False
    retval = globals()['gChoices_flatten'][code] if code in globals()['gChoices_flatten'] else None
    if retval is None:
        retval = replaceComponent(code,model)
        replaced = True
    else:
        if retval['stock1'] == 0:
            retval = replaceComponent(code,model)
            replaced = True
    # there is 1 thing downwhere count! is is installed just in this component!
    ret = deepcopy(retval)
    ret['replaced'] = replaced
    return ret



class ComponentForModelsPage(object):
    def __init__(self,model,component, cat_name, price):
        self.component= component
        self.price = price
        self.cat_name = cat_name
        self.model = model
    def getIconUrl(self):
        retval = "/static/icon.png"
        if 'description' in self.component and'imgs' in self.component['description']:
            retval = ''.join(("/image/",self.component['_id'],"/",
                              self.component['description']['imgs'][0],'.jpg'))
        return retval
    def render(self):
        li = etree.Element('li')
        li.text = self.component['text'] + u' <strong>'+ unicode(self.price) + u' р</strong>'
        li.set('id',self.model['_id']+'_'+self.component['_id'])
        return li

# TODO! refactor it without side effects
# TODO! rename it. it is absoluttely about no prices!
def buildPrices(model, json_prices, price_span):
    aliasses_reverted = {}
    total = 0
    __components = []
    for k,v in parts_aliases.items():
        aliasses_reverted.update({v:k})
    def updatePrice(_id, catalogs, required_catalogs, price):
        if catalogs == required_catalogs:
            if _id in json_prices:
                json_prices[_id].update({aliasses_reverted[required_catalogs]:price})
            else:
                json_prices[_id] = {aliasses_reverted[required_catalogs]:price}

    for cat_name,code in model['items'].items():
        count = 1
        if type(code) is list:
            count = len(code)
            code = code[0]
        component_doc = findComponent(model,cat_name)
        code = component_doc['_id']
        price = makePrice(component_doc)*count
        total += price
        updatePrice(model['_id'],cat_name,displ,price)
        updatePrice(model['_id'],cat_name,soft,price)
        updatePrice(model['_id'],cat_name,audio,price)
        updatePrice(model['_id'],cat_name,mouse,price)
        updatePrice(model['_id'],cat_name,kbrd,price)
        __components.append(ComponentForModelsPage(model,component_doc, cat_name, price))
    total += INSTALLING_PRICE + BUILD_PRICE+DVD_PRICE
    price_span.text = str(total) + u' р'
    json_prices[model['_id']]['total'] = total
    return sorted(__components, lambda c1,c2:parts[c1.cat_name]-parts[c2.cat_name])



def index(template, skin, request):

    if globals()['gChoices'] is None:
        d = fillChoices()
        d.addCallback(lambda some: index(template, skin, request))
        return d

    def render(result):
        i = 0
        models = sorted([row['doc'] for row in result['rows']],lambda x,y: x['order']-y['order'])
        tree = template.root()
        div = template.middle.xpath('//div[@id="computers_container"]')[0]
        json_prices = {}
        # TODO! make model view as for ComponentForModelsPage!!!!!!!!
        for m in models:
            model_snippet = tree.find('model')
            snippet = deepcopy(model_snippet.find('div'))
            snippet.set('style',"background-image:url('" + imgs[i] + "')")
            a = snippet.find('.//a')
            a.set('href','/computer/%s' % m['_id'])
            a.text=m['name']
            price_span = snippet.find('.//span')
            price_span.set('id',m['_id'])
            buildPrices(m, json_prices, price_span)
            div.append(snippet)
            i+=1
            if i==len(imgs): i=0
        template.middle.find('script').text = 'var prices=' + simplejson.dumps(json_prices) + ';'
        last_update = template.middle.xpath('//span[@id="last_update"]')[0]
        now = datetime.now()
        hour = now.hour+7
        if hour>18:
            last_update.text = '.'.join((str(now.day),str(now.month),str(now.year)[2:])) +' 18:20'
        elif hour<9:
            delta = timedelta(days=-1)
            now = now + delta
            last_update.text = '.'.join((str(now.day),str(now.month),str(now.year)[2:])) +' 18:20'
        else:
            if now.minute<14:
                hour-=1
            last_update.text = '.'.join((str(now.day),str(now.month),str(now.year)[2:])) +\
                ' '+str(hour)+':' + str(14+randint(1,6))
        
        skin.top = template.top
        skin.middle = template.middle
        return skin.render()

    d = couch.openView(designID,'models',include_docs=True,stale=False)
    d.addCallback(render)
    return d


def updateOriginalModelPrices():
    def update(models):
        for row in models['rows']:
            model = row['doc']
            model['original_prices'] = {}
            for name,code in model['items'].items():
                if type(code) is list:
                    code = code[0]
                if code in globals()['gChoices_flatten']:
                    component = globals()['gChoices_flatten'][code]
                    model['original_prices'].update({code:component['price']})
                else:
                    model['original_prices'].update({code:99})
            couch.saveDoc(model)
    d = couch.openView(designID,'models',include_docs=True,stale=False)
    d.addCallback(update)
