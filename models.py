# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from lxml import etree
from twisted.internet import defer
from string import Template
from urllib import quote_plus, unquote_plus
import simplejson
import re
from copy import deepcopy

# <catalog id="7388" name="Материнские платы">
#       <catalog id="17961" name="LGA1155">
#       <catalog id="12854" name="LGA1156">
#       <catalog id="18029" name="LGA1366 Dual Core (процессоры Intel Nehalem )">
#       <catalog id="7449" name="LGA775 Dual Core (процессоры Intel)">
#       <catalog id="7627" name="SOCKET 478">
#       <catalog id="7699" name="SOCKET AM2 3 (процессоры AMD)">
#      <catalog id="2899" name="Материнские платы с процессором">

# <catalog id="7399" name="Процессоры">
#        <catalog id="18027" name="LGA1155">
#        <catalog id="18028" name="LGA1156">
#        <catalog id="9422" name="LGA1366">
#        <catalog id="7451" name="LGA775 Dual&amp;Quad Core">
#        <catalog id="7700" name="SOCKET AM2">

components = "7363"
perifery = "7365"


procs = "7399"
mothers = "7388"

mothers_1155 = [components, mothers,"17961"]
mothers_1156 = [components,mothers,"12854"]
mothers_1366 =[components,mothers,"18029"]
mothers_775 = [components,mothers,"7449"]
mothers_am23 = [components,mothers,"7699"]
mothers_fm1 = [components,mothers,"19238"]

videos = "7396"

geforce = [components,videos,"7607"]
radeon = [components,videos,"7613"]

rams = "7394"
ddr3 = [components, rams, "11576"]
ddr2 = [components, rams, "7711"]
so_dim = [components, rams,"16993"]

hdds = "7406"
satas = [components, hdds,"7673"]
ides = [components, hdds,"7564"]
cases = [components, hdds,"7383"]

cases = "7383"
cases_400_650 = [components,cases,"7459"]
cases_exclusive = [components,cases, "10837"]

displays = "7384"
displays_19_20 = [components,displays,"7526"]
displays_22_26 = [components,displays,"13209"]


kbrds = "7387"
kbrds_a4 = [perifery,kbrds,"14092"]
kbrds_acme = [perifery,kbrds,"7593"]
kbrds_chikony = [perifery,kbrds,"17396"]
kbrds_game = [perifery,kbrds,"18450"]


mouses = "7390"
mouses_a4 = [perifery,mouses,"7603"]
mouses_genius = [perifery,mouses,"15844"]
mouses_acme = [perifery,mouses,"14320"]
mouses_game = [perifery,mouses,"7582"]

sound = "7413"
sound_internal = [components,sound,"8012"]

network = "7405"
lans = [network,"14710"]

procs_1155 = [components, procs, "18027"]
procs_1156 = [components,procs,"18028"]
procs_1366 = [components,procs,"9422"]
procs_775 = [components,procs,"7451"]
procs_am23 = [components,procs,"7700"]
procs_fm1 =  [components,procs,"19257"]


audio_20 = ["7365","7389", "7447"]
audio_21 = ["7365","7389", "7448"]
audio_51 = ["7365","7389", "7462"]

windows = ["7369","14570","14571"]

mother_to_proc_mapping= [
    (mothers_1155,procs_1155),
    (mothers_1156,procs_1156),
    (mothers_1366,procs_1366),
    (mothers_775,procs_775),
    (mothers_am23,procs_am23),
    (mothers_fm1,procs_fm1)
    ]



def getCatalogsKey(doc):
    cats = []
    for c in doc['catalogs']:
        cats.append(str(c['id']))
    return cats


# def isMother(doc, cats=None):
#     if cats is None:
#         cats = getCatalogsKey(doc)
#     return components in cats and mothers in cats


# def isProc(doc, cats=None):
#     if cats is None:
#         cats = getCatalogsKey(doc)
#     return components in cats and mothers in cats



models = [
    {'name':u"Локалхост",
     'items':   {'mother':'19005', 'proc':'18984', 'video':'18802', 'ram':['17575'],'hdd':'10661', 'case':'19165',
                 'displ':'15252', 'kbrd':'16499', 'mouse':'15976', 'sound':None, 'lan':None, 'windows':'14439', 'audio':"8610"},
     'price':6500,
     "socket":"1155"
     },
    {'name':u"Браузер",
     'items':   {'mother':'19005', 'proc':'18984', 'video':'18802', 'ram':['17575'],'hdd':'10661', 'case':'19165',
                 'displ':'15252', 'kbrd':'16499', 'mouse':'15976', 'sound':None, 'lan':None, 'windows':'14439', 'audio':"8610"},
     'price':8500,
     "socket":"1155"
     },
    {'name':u"Принтер",
     'items':   {'mother':'19005', 'proc':'18984', 'video':'18802', 'ram':['17575'],'hdd':'10661',
                 'case':'19165', 'displ':'15252', 'kbrd':'16499', 'mouse':'15976', 'sound':None, 'lan':None, 'windows':'14439', 'audio':"8610"},
     'price':15200,
     "socket":"1155"
     },
    {'name':u"Числодробилка",
     'items':   {'mother':'19162', 'proc':'18137', 'video':'18994', 'ram':['17970','17970','17970','17970'],'hdd':'16991',
                 'case':'18219', 'displ':'15606', 'kbrd':'16499', 'mouse':'15976','sound':None, 'lan':None, 'windows':'14439', 'audio':"8610"},
     'price':32000,
     "socket":"1155"
     }
]

def getModelComponents(model):
    for k,v in model['items'].items():
        if type(v) is list:
            for el in v:
                yield el
        else:
            yield v

def component_name(_id, model):
    for k,v in model['items'].items():
        if type(v) is list:
            for el in v:
                if el==_id:
                    return k
        else:
            if v==_id:
                return k



Margin=1.2
Course = 29.5

def makePrice(doc):
    course = Course
    # cats = getCatalogsKey(doc)
    # isWindows = len(filter(lambda x: x[0] == x[1],zip(windows,cats))) == len(cats)

    if getCatalogsKey(doc) == windows:
        course = 1
    our_price = doc['price']*Margin*course
    doc['price'] = int(str(round(our_price)).split('.')[0])
    return doc


def cleanDoc(doc):
    def pop(token):
        if token in doc:
            doc.pop(token)
    for t in ['text', '_attachments','description','flags','inCart','ordered','reserved','stock1', '_rev', 'warranty_type']:#
        pop(t)
    if 'catalogs' in doc:
        for c in doc['catalogs']:
            if 'name' in c:
                c.pop('name')
    return doc

imgs = ['static/acer-aspire-ie-3450-desktop-pc-1.png',
        'static/compaq-presario-sg3440il-desktop-pc1.png',
        'static/dell-studio-hybrid-desktop-pc1.png',
        'static/desktop-pc1.png'
        ]





def renderModelForIndex(result, template, m, image_i):
    # CACHE ALL MODELS HERE!!!
    tree = template.root()
    m.update({'item_docs':result})
    model_snippet = tree.find('model')

    snippet = deepcopy(model_snippet.find('div'))
    snippet.set('style',"background-image:url('" + imgs[image_i] + "')")
    a = snippet.find('.//a')
    a.set('href','/desktop/%s' % m['name'])
    a.text=m['name']
    snippet.find('.//span').text=(unicode(m['price']) + u' р')
    return snippet

def index(template, skin, request):
    i = 0
    defs = []
    for m in models:
        d = couch.listDoc(keys=[c for c in getModelComponents(m)],include_docs=True)
        d.addCallback(renderModelForIndex, template, m, i)
        defs.append(d)
        i+=1
        if i==len(imgs): i=0

    def _render(res,_template,_skin):
        div = _template.middle.find('div')
        for el in res:
            if el[0]:
                div.append(el[1])
        for el in _template.root().find('leftbutton'):
            div.append(el)
        _skin.top = _template.top
        _skin.middle = _template.middle
        return skin.render()

    d = defer.DeferredList(defs)
    d.addCallback(_render, template, skin)
    return d





parts = {'mother':0, 'proc':10, 'video':20, 'hdd':30, 'ram':40, 'case':50, 'sound':70, 'lan':80, 'displ':90, 'audio':100, 'windows':110, 'kbrd':120, 'mouse':130, 'audio':140}
parts_names = {'proc':u'Процессор', 'ram':u'Память', 'video':u'Видеокарта', 'hdd':u'Жесткий диск', 'case':u'Корпус','sound':u'Звуковая карта',
               'lan':u'Сетевая карта', 'mother':u'Материнская плата','displ':u'Монитор', 'audio':u'Аудиосистема', 'kbrd':u'Клавиатура', 'mouse':u'Мышь' }



def replaceComponent(code, choices, name, socket):
    flatten = []
    
    def sameCatalog(doc):
        retval = True
        if name in ['mother','proc']:
            retval = False
            cats = name + 's_' + socket
            real_cats = globals()[cats]
            retval = getCatalogsKey(doc) == real_cats
        return retval

    if type(choices) is list:
        for el in choices:
            if el[0]:
                for ch in el[1][1]['rows']:
                    if sameCatalog(ch['doc']):
                        flatten.append(ch['doc'])
    else:
        for ch in choices['rows']:
            flatten.append(ch['doc'])

    keys = [doc['id'] for doc in flatten]
    keys.append(code)
    keys = sorted(keys)
    _length = len(keys)
    ind = keys.index(code)
    _next = ind+1
    if _next == _length:
        _next = ind-1
    next_el = deepcopy(flatten[_next])
    return next_el

def renderComputer(components_choices, template, skin, model):

    def makeOption(row):
        try:
            option = etree.Element('option')
            if 'font' in row['doc']['text']:
                row['doc']['text'] = re.sub('<font.*</font>', '',row['doc']['text'])
                row['doc'].update({'featured':True})
            option.text = row['doc']['text']

            option.text +=u' ' + unicode(row['doc']['price']) + u' р'
            
            option.set('value',row['id'])
            return option
        except:
            print row
    def appendOptions(options, container):
        for o in sorted(options, lambda x,y: x[1]-y[1]):
            container.append(o[0])

    def noComponent(name, component_doc, rows):
        if name in ['mouse','kbrd','displ','windows', 'audio']:
            no_name = 'no' + name
            no_component_doc = deepcopy(component_doc)
            no_component_doc['_id'] = no_name
            no_component_doc['price'] = 0
            no_component_doc['text'] = u'нет'
            rows.insert(0,{'id':no_name, 'key':no_name,'doc':no_component_doc})


    template.top.find('div').find('h2').text = model['name']

    original_viewlet = template.root().find('componentviewlet')
    components= components_choices[0]
    choices = components_choices[1]

    model_json = {}
    model_parts = {}
    tottal = 0
    components_json = {}
    viewlets = []

    # description_json = {}
    for name,code in model['items'].items():
        if code is None: continue
        if type(code) is list: code = code[0]
        viewlet = deepcopy(original_viewlet)
        component_doc = [r['doc'] for r in components['rows'] if r['id'] == code][0]
        if component_doc is None:
            component_doc = replaceComponent(code, choices[name], name, model['socket'])
        else:
            if component_doc['stock1'] == 0:
                component_doc = replaceComponent(code, choices[name], name, model['socket'])
        component_doc = makePrice(component_doc)
        tr = viewlet.find("tr")
        tr.set('id',name)
        body = viewlet.xpath("//td[@class='body']")[0]
        body.set('id',component_doc['_id'])
        body.text = re.sub('<font.*</font>', '',component_doc['text'])

        descr = etree.Element('div')
        descr.set('class','description')
        d_comments = ''
        d_name = ''
        if 'description' in component_doc:
            d_name = component_doc['description']['name']
            d_comments = component_doc['description']['comments']
        descr.text =  d_name + d_comments

        tottal += component_doc['price']

        component_doc = cleanDoc(component_doc)
        model_json.update({component_doc['_id']:component_doc})
        model_parts.update({component_doc['_id']:name})


        #TODO! now. when replacement is taking place, it need to check mother and proc!

        viewlet.xpath('//td[@class="component_price"]')[0].text = unicode(component_doc['price']) + u' р'

        select = viewlet.xpath("//td[@class='component_select']")[0].find('select')

        ch = choices[name]
        options = []
        if type(ch) is list:
            noComponent(name, component_doc, ch[0][1][1]['rows'])
            for el in ch:
                if el[0]:
                    option_group = etree.Element('optgroup')
                    option_group.set('label', el[1][0])
                    _options = []
                    for r in el[1][1]['rows']:
                        r['doc'] = makePrice(r['doc'])
                        option = makeOption(r)
                        if r['id'] == component_doc['_id']:
                            option.set('selected','selected')
                        _options.append((option, r['doc']['price']))
                        r['doc'] = cleanDoc(r['doc'])
                        components_json.update({r['doc']['_id']:r['doc']})
                    appendOptions(_options, option_group)
                    options.append((option_group, 0))
        else:
            noComponent(name, component_doc, ch['rows'])
            for row in ch['rows']:
                row['doc'] = makePrice(row['doc'])
                option = makeOption(row)
                options.append((option, row['doc']['price']))
                if row['id'] == component_doc['_id']:
                    option.set('selected','selected')
                row['doc'] = cleanDoc(row['doc'])
                components_json.update({row['doc']['_id']:row['doc']})

        appendOptions(options, select)
        viewlets.append((parts[name],viewlet,descr))


    components_container = template.middle.xpath('//table[@id="components"]')[0]
    description_container = template.middle.xpath('//div[@id="descriptions"]')[0]

    for viewlet in sorted(viewlets, lambda x,y: x[0]-y[0]):
        components_container.append(viewlet[1].find('tr'))
        description_container.append(viewlet[2])

    template.middle.find('script').text = u''.join(('var model=',simplejson.dumps(model_json),
                                                    ';var tottal=',unicode(tottal),
                                                    ';var choices=',simplejson.dumps(components_json),
                                                    ';var model_parts=', simplejson.dumps(model_parts),
                                                    ';var parts_names=',simplejson.dumps(parts_names),
                                                    ';var mother_to_proc_mapping=',simplejson.dumps(mother_to_proc_mapping),
                                                    ';var proc_to_mother_mapping=',simplejson.dumps([(el[1],el[0]) for el in mother_to_proc_mapping])
                                                    ))
    template.top.xpath("//span[@id='large_price']")[0].text = unicode(tottal +800)
    template.top.xpath("//strong[@id='baseprice']")[0].text = unicode(tottal + 800)
    skin.top = template.top
    skin.middle = template.middle
    skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 280px;')
    skin.root().xpath('//div[@id="middle"]')[0].set('style',' margin: -40px auto;padding: 0;width:1000px')
    return skin.render()


from twisted.python import log
import sys

def pr(some):
    log.startLogging(sys.stdout)
    log.msg(some)
    return some


printed = False


def fillChoices(result):
    # docs = [r['doc'] for r in result['rows'] if r['key'] is not None]
    defs = []
    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mothers_1366, stale=False)
                                    .addCallback(lambda res: ("LGA1366",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mothers_1155, stale=False)
                                    .addCallback(lambda res: ("LGA1155",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mothers_1156, stale=False)
                                    .addCallback(lambda res: ("LGA1166",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mothers_775, stale=False)
                                    .addCallback(lambda res: ("LGA775",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mothers_am23, stale=False)
                                    .addCallback(lambda res: ("AM2 3",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mothers_fm1, stale=False)
                                    .addCallback(lambda res: ("FM1",res))
                                    ])
                .addCallback(lambda res: {"mother":res}))


    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True,key=procs_1155, stale=False)
                                    .addCallback(lambda res:('LGA1155',res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True,key=procs_1156, stale=False)
                                                   .addCallback(lambda res:('LGA1156',res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True,key=procs_1366, stale=False)
                                                   .addCallback(lambda res:('LGA1366',res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True,key=procs_am23, stale=False)
                                    .addCallback(lambda res:('AM2 3',res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True,key=procs_775, stale=False)
                                                   .addCallback(lambda res:('LGA7755',res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=procs_fm1, stale=False)
                                    .addCallback(lambda res: ("FM1",res))
                                    ])

                .addCallback(lambda res: {"proc":res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=geforce, stale=False)
                                    .addCallback(lambda res: (u"GeForce",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=radeon, stale=False)
                                    .addCallback(lambda res: (u"Radeon",res))])
                .addCallback(lambda res: {"video":res}))

    defs.append(couch.openView(designID,
                               'catalogs',include_docs=True, key=ddr3, stale=False)
                .addCallback(lambda res: {"ram":res}))
    defs.append(couch.openView(designID,
                               'catalogs',include_docs=True, key=satas, stale=False)
                .addCallback(lambda res: {"hdd":res}))
    defs.append(couch.openView(designID,
                               'catalogs',include_docs=True, key=windows, stale=False)
                .addCallback(lambda res: {"windows":res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=cases_400_650, stale=False)
                                    .addCallback(lambda res: (u"Корпусы 400-650 Вт",res)),
                                   couch.openView(designID,
                                                  'catalogs',include_docs=True, key=cases_exclusive, stale=False)
                                    .addCallback(lambda res: (u"Эксклюзивные корпусы",res))])
                .addCallback(lambda res: {"case":res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=displays_19_20, stale=False)
                                    .addCallback(lambda res: (u"Мониторы 19-20 дюймов",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=displays_22_26, stale=False)
                                    .addCallback(lambda res: (u"Мониторы 22-26 дюймов",res))])
                .addCallback(lambda res: {"displ":res}))


    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrds_a4, stale=False)
                                    .addCallback(lambda res: (u"Клавиатуры A4Tech",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrds_acme, stale=False)
                                    .addCallback(lambda res: (u"Клавиатуры Acme",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrds_chikony, stale=False)
                                    .addCallback(lambda res: (u"Клавиатуры Chikony",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrds_game, stale=False)
                                    .addCallback(lambda res: (u"Игровые Клавиатуры",res)),])
                .addCallback(lambda res: {"kbrd":res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouses_a4, stale=False)
                                    .addCallback(lambda res: (u"Мыши A4Tech",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouses_game, stale=False)
                                    .addCallback(lambda res: (u"Игровые Мыши",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouses_acme, stale=False)
                                    .addCallback(lambda res: (u"Мыши Acme",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouses_genius, stale=False)
                                    .addCallback(lambda res: (u"Мыши Genius",res))])
                .addCallback(lambda res: {"mouse":res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=audio_20, stale=False)
                                    .addCallback(lambda res: (u"Аудио системы 2.0",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=audio_21, stale=False)
                                    .addCallback(lambda res: (u"Аудио системы 2.1",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=audio_51, stale=False)
                                    .addCallback(lambda res: (u"Аудио системы 5.1",res))])
                .addCallback(lambda res: {"audio":res}))
    def makeDict(res):
        new_res = {}
        for el in res:
            if el[0]:
                new_res.update(el[1])
        return new_res
    #TODO - this callbaqck to the higher level
    return defer.DeferredList(defs).addCallback(makeDict).addCallback(lambda choices: (result, choices))

def computer(template, skin, request):
    name = unicode(unquote_plus(request.path.split('/')[-1]), 'utf-8')
    _models = [m for m in models if m['name'] == name]
    model = _models[0] if len(_models)>0 else models[0]
    keys = [c for c in getModelComponents(model) if c is not None]
    d = couch.listDoc(keys=keys,include_docs=True)
    d.addCallback(fillChoices)
    d.addCallback(renderComputer, template, skin, model)
    return d
