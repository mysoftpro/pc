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

mother_to_proc_mapping= {
    tuple(mothers_1155):[components, procs, "18027"],
    tuple(mothers_1156):[components,procs,"18028"],
    tuple(mothers_1366):[components,procs,"9422"],
    tuple(mothers_775):[components,procs,"7451"],
    tuple(mothers_am23):[components,procs,"7700"]
    }


def getCatalogsKey(doc):
    cats = []
    for c in doc['catalogs']:
        cats.append(c['id'])
    return cats


def isMother(doc):
    cats = getCatalogsKey(doc)#[c['id'] for c in doc['catalogs']]
    return components in cats and mothers in cats




models = [
    {'name':u"Локалхост",
     'items':   {'mother':'19005', 'proc':'18984', 'video':'18802', 'ram':['17575'],'hdd':'10661', 'case':'19165', 'displ':'15252', 'kbrd':None, 'mouse':None, 'sound':None, 'lan':None},
     'price':6500
     },
    {'name':u"Браузер",
     'items':   {'mother':'19005', 'proc':'18984', 'video':'18802', 'ram':['17575'],'hdd':'10661', 'case':'19165', 'displ':'15252', 'kbrd':None, 'mouse':None, 'sound':None, 'lan':None},
     'price':8500
     },
    {'name':u"Принтер",
     'items':   {'mother':'19005', 'proc':'18984', 'video':'18802', 'ram':['17575'],'hdd':'10661', 'case':'19165', 'displ':'15252', 'kbrd':None, 'mouse':None, 'sound':None, 'lan':None},
     'price':15200
     },
    {'name':u"Числодробилка",
     'items':   {'mother':'19162', 'proc':'18137', 'video':'18994', 'ram':['17970','17970','17970','17970'],'hdd':'16991', 'case':'18219', 'displ':'15606', 'kbrd':None, 'mouse':None, 'sound':None, 'lan':None},
     'price':32000
     }
]

def getModelComponents(model):
    for v in model['items'].values():
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



Margin=1.25
Course = 29

def makePrice(doc):
    our_price = doc['price']*Margin*Course
    doc['price'] = int(str(round(our_price)).split('.')[0])
    return doc


def cleanDoc(doc):
    def pop(token):
        if token in doc:
            doc.pop(token)
    for t in ['text', '_attachments','description','flags','inCart','ordered','reserved','stock1']:#'warranty_type'
        pop(t)
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
    a.set('href','/computer/%s' % m['name'])
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





parts = {'mother':u'Материнская плата', 'proc':u'Процессор', 'video':u'Видео', 'ram':u'Память', 'hdd':u'Жесткий диск', 'case':u'Корпус', 'kbrd':u'Клавиатура', 'mouse':u'Мышь', 'displ':u'Монитор'}

def renderComputer(components_choices, template, skin, model):

    def makeOption(row, select):
        option = etree.Element('option')
        if 'font' in row['doc']['text']:
            row['doc']['text'] = re.sub('<font.*</font>', '',row['doc']['text'])
            row['doc'].update({'featured':True})
        option.text = row['doc']['text'] + u' ' + unicode(row['doc']['price']) + u' р'
        option.set('value',row['id'])
        select.append(option)
        return option
    template.top.find('h2').text = model['name']    
    
    original_viewlet = template.root().find('componentviewlet')
    components= components_choices[0]
    choices = components_choices[1]        
    
    model_json = {}
    tottal = 0
    components_json = {}

    for name,code in model['items'].items():        
        if code is None: continue
        if type(code) is list: code = code[0]
        viewlet = deepcopy(original_viewlet)
        component_doc = [r['doc'] for r in components['rows'] if r['id'] == code][0]
        component_doc = makePrice(component_doc)
        viewlet.xpath('//div[@class="component_tab"]')[0].text = parts[name]        
        for div in viewlet.xpath("//div[@class='toptools']"):
            div.find('span').text = unicode(component_doc['price']) + u' р'
        viewlet.xpath("//div[@class='body']")[0].text = component_doc['text']
        tottal += component_doc['price']        
        model_json.update({component_doc['_id']:component_doc})
        
        select = viewlet.xpath("//div[@class='component_select']")[0].find('select')                
        ch = choices[name]
        if type(ch) is list:
            for el in ch:
                if el[0]:
                    option_group = etree.Element('optgroup')
                    option_group.set('label', el[1][0])
                    for r in el[1][1]['rows']:
                        r['doc'] = makePrice(r['doc'])
                        option = makeOption(r, option_group)
                        if r['id'] == code:
                            option.set('selected','selected')                            
                        r['doc'] = cleanDoc(r['doc'])
                        components_json.update({r['doc']['_id']:r['doc']})

                    select.append(option_group)
        else:
            for row in ch['rows']:
                option = makeOption(row, select)                
                if row['id'] == code:
                    option.set('selected','selected')
                row['doc'] = cleanDoc(row['doc'])
                components_json.update({row['doc']['_id']:row['doc']})
        template.top.xpath('//div[@id="components"]')[0].append(viewlet)
    
    template.middle.find('script').text = u''.join(('var model=',simplejson.dumps(model_json),';var tottal=',unicode(tottal),u';var choices=',simplejson.dumps(components_json),';'))
    template.top.xpath("//span[@id='large_price']")[0].text = unicode(model['price'])
    template.top.xpath("//span[@id='oldprice']")[0].text = unicode(model['price'])
    template.top.xpath("//span[@id='newprice']")[0].text = unicode(model['price'])
    skin.top = template.top
    skin.middle = template.middle
    return skin.render()


from twisted.python import log
import sys

def pr(some):
    log.startLogging(sys.stdout)
    log.msg(some)
    return some


printed = False


def fillChoices(result):
    docs = [r['doc'] for r in result['rows'] if r['key'] is not None]
    defs = []
    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mothers_1366)
                                    .addCallback(lambda res: ("LGA1366",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mothers_1155)
                                    .addCallback(lambda res: ("LGA1155",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mothers_1156)
                                    .addCallback(lambda res: ("LGA1166",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mothers_775)
                                    .addCallback(lambda res: ("LGA775",res)),
                                    couch.openView(designID,
                                                   'catalogs',
                                                   include_docs=True, key=mothers_am23)
                                    .addCallback(lambda res: ("AM2 3",res))])
                .addCallback(lambda res: {"mother":res}))

    mother = [d for d in docs if isMother(d)][0]
    mother_cats = getCatalogsKey(mother)

    defs.append(couch.openView(designID,
                               'catalogs',
                               include_docs=True,
                               key=mother_to_proc_mapping[tuple(mother_cats)]).addCallback(lambda res: {"proc":res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=geforce)
                                    .addCallback(lambda res: (u"GeForce",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=radeon)
                                    .addCallback(lambda res: (u"Radeon",res))])
                .addCallback(lambda res: {"video":res}))

    defs.append(couch.openView(designID,
                               'catalogs',include_docs=True, key=ddr3).addCallback(lambda res: {"ram":res}))
    defs.append(couch.openView(designID,
                               'catalogs',include_docs=True, key=satas).addCallback(lambda res: {"hdd":res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=cases_400_650)
                                    .addCallback(lambda res: (u"Корпусы 400-650 Вт",res)),
                                   couch.openView(designID,
                                                  'catalogs',include_docs=True, key=cases_exclusive)
                                    .addCallback(lambda res: (u"Эксклюзивные корпусы",res))])
                .addCallback(lambda res: {"case":res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=displays_19_20)
                                    .addCallback(lambda res: (u"Мониторы 29-20 дюймов",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=displays_22_26)
                                    .addCallback(lambda res: (u"Мониторы 22-26 дюймов",res))])
                .addCallback(lambda res: {"displ":res}))


    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrds_a4)
                                    .addCallback(lambda res: (u"Клавиатуры A4Tech",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrds_acme)
                                    .addCallback(lambda res: (u"Клавиатуры Acme",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrds_chikony)
                                    .addCallback(lambda res: (u"Клавиатуры Chikony",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrds_game)
                                    .addCallback(lambda res: (u"Игровые Клавиатуры",res)),])
                .addCallback(lambda res: {"kbrd":res}))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouses_a4)
                                    .addCallback(lambda res: (u"Мыши A4Tech",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouses_game)
                                    .addCallback(lambda res: (u"Игровые Мыши",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouses_acme)
                                    .addCallback(lambda res: (u"Мыши Acme",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouses_genius)
                                    .addCallback(lambda res: (u"Мыши Genius",res))])
                .addCallback(lambda res: {"mouse":res}))
    def makeDict(res):
        new_res = {}
        for el in res:
            if el[0]:
                new_res.update(el[1])
        return new_res
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
