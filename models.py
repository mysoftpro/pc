# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from lxml import etree
from twisted.internet import defer
from string import Template
from urllib import quote_plus, unquote_plus
import simplejson
import re

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
kbrds_a4 = [components,kbrds,"14092"]
kbrds_acme = [components,kbrds,"14092"]
kbrds_chikony = [components,kbrds,"17396"]
kbrds_game = [components,kbrds,"18450"]


mouses = "7390"
mouses_a4 = [components,mouses,"7603"]
mouses_genius = [components,mouses,"15844"]
mouses_acme = [components,mouses,"14320"]
mouses_game = [components,mouses,"7582"]

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
     'items':   {'mother':'19005', 'proc':'18984', 'video':'18802', 'ram':['17575'],'hdd':'10661', 'case':'19165', 'displ':'15252', 'kbrd':'16499', 'mouse':'15998', 'sound':None, 'lan':None},
     'price':6500
     },
    {'name':u"Браузер",
     'items':   {'mother':'19005', 'proc':'18984', 'video':'18802', 'ram':['17575'],'hdd':'10661', 'case':'19165', 'displ':'15252', 'kbrd':'16499', 'mouse':'15998', 'sound':None, 'lan':None},
     'price':8500
     },
    {'name':u"Принтер",
     'items':   {'mother':'19005', 'proc':'18984', 'video':'18802', 'ram':['17575'],'hdd':'10661', 'case':'19165', 'displ':'15252', 'kbrd':'16499', 'mouse':'15998', 'sound':None, 'lan':None},
     'price':15200
     },
    {'name':u"Числодробилка",
     'items':   {'mother':'19162', 'proc':'18137', 'video':'18994', 'ram':['17970','17970','17970','17970'],'hdd':'16991', 'case':'18219', 'displ':'15606', 'kbrd':'11383', 'mouse':'18185', 'sound':None, 'lan':None},
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
    if 'text' in doc:
        doc.pop('text')
    if '_attachments' in doc:
        doc.pop('_attachments')
    return doc

imgs = ['static/acer-aspire-ie-3450-desktop-pc-1.png',
        'static/compaq-presario-sg3440il-desktop-pc1.png',
        'static/dell-studio-hybrid-desktop-pc1.png',
        'static/desktop-pc1.png'
        ]


from copy import deepcopy

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
    snippet.find('.//span').text=(unicode(m['price']) + u' руб')
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






def renderComputer(components_choices, template, skin, model):
    def makeOption(row, select):
        option = etree.Element('option')
        if 'font' in row['doc']['text']:
            row['doc']['text'] = re.sub('<font.*</font>', '',row['doc']['text'])
            row['doc'].update({'featured':True})
        option.text = row['doc']['text'] + u' ' + unicode(row['doc']['price']) + u' руб'
        option.set('value',row['id'])
        select.append(option)
        return option

    components= components_choices[0]
    choices = components_choices[1]
    viewlet = deepcopy(template.root().find('componentviewlet'))
    print viewlet
    for name,code in model['items'].items():
        if code is None: continue
        if type(code) is list: code = code[0]
        component_doc = [r['doc'] for r in components['rows'] if r['id'] == code][0]
        component_doc = makePrice(component_doc)
        viewlet.xpath("//span[@id='component_old_price']")[0].text = unicode(component_doc['price'])
        viewlet.xpath("//span[@id='component_new_price']")[0].text = unicode(component_doc['price'])
        viewlet.xpath("//div[@class='component_body']")[0].text = component_doc['text']

        for ch in choices:
            if ch[0] and ch[1][0] == name :
                select = viewlet.xpath("//div[@class='component_select']")[0].find('select')
                if type(ch[1][1]) is list:
                    for el in ch[1][1]:
                        if el[0]:
                            option_group = etree.Element('optgroup')
                            option_group.set('label', el[1][0])
                            for r in el[1][1]['rows']:
                                r['doc'] = makePrice(r['doc'])
                                option = makeOption(r, option_group)
                                if r['id'] == code:
                                    option.set('selected','selected')
                                # r['doc'] = cleanDoc(r['doc'])
                                # json.update({r['doc']['_id']:r['doc']})
                            select.append(option_group)
                else:
                    for row in ch[1][1]['rows']:
                        option = makeOption(row, select)
                        # json.update({r['doc']['_id']:r['doc']})
                        if row['id'] == code:
                            option.set('selected','selected')
    
            break
        template.middle.append(viewlet)
    skin.top = template.top
    skin.middle = template.middle
    return skin.render()

    # top = template.top
    # top.find("h2").text = model['name']
    # json = {}
    # tottal = 0
    # for r in items['rows']:
    #     if r['key'] is None: continue
    #     _id = r['id']
    #     td_exp = "//td[@id='" + component_name(_id, model) + "']"
    #     td_found = top.xpath(td_exp)
    #     if len(td_found)>0:
    #         if 'font' in r['doc']['text']:
    #             r['doc']['text'] = re.sub('<font.*</font>', '',r['doc']['text'])
    #             r['doc'].update({'featured':True})
    #         td_found[0].text = r['doc']['text']
    #         r['doc'] = makePrice(r['doc'])
    #         td_found[0].getnext().text = unicode(r['doc']['price'])  + u' руб'
    #         tottal += r['doc']['price']
    #         r['doc'] = cleanDoc(r['doc'])
    #         json.update({r['doc']['_id']:r['doc']})

    # top.xpath("//span[@id='newprice']")[0].text = unicode(tottal)
    # top.xpath("//span[@id='oldprice']")[0].text = unicode(tottal)

    # template.middle.find('script').text += u''.join(('var model=',simplejson.dumps(json),';var tottal=',unicode(tottal)))
    # skin.top = template.top
    # skin.middle = template.middle
    # return skin.render()


from twisted.python import log
import sys

def pr(some):
    log.startLogging(sys.stdout)
    log.msg(some)
    return some

# def delayedRes(res):
#     def delayed(some):
#         li = list(some)
#         li.insert(0,res)
#         return tuple(li)
#     return delayed

printed = False

def renderChoices(choices, template, skin, model):
    # json = {}
    json = {}
    model_ids = [i for i in getModelComponents(model)]
    def makeOption(row, select, td):
        option = etree.Element('option')
        if 'font' in row['doc']['text']:
            row['doc']['text'] = re.sub('<font.*</font>', '',row['doc']['text'])
            row['doc'].update({'featured':True})
        option.text = row['doc']['text'] + u' ' + unicode(row['doc']['price']) + u' руб'
        option.set('value',row['id'])
        if row['id'] in model_ids:
            option.set('selected','selected')
            if 'description' not in row['doc']:
                return
            if 'comments' not in row['doc']['description']:
                return
            td.getnext().text = unicode(row['doc']['price']) + u' руб'
            base_descriptions = template.middle.xpath("//td[@id='description_base']")
            base_descriptions[0].text = row['doc']['description']['name'] + row['doc']['description']['comments']
            new_descriptions = template.middle.xpath("//td[@id='description_new']")
            new_descriptions[0].text = row['doc']['description']['name'] + row['doc']['description']['comments']

        select.append(option)

    top = template.top
    for c in choices:
        if not c[0]: continue
        token = c[1][0]
        td_exp = "//td[@id='" + token + "']"
        td_found = top.xpath(td_exp)
        if len(td_found)>0:
            select = etree.Element('select')
            if type(c[1][1]) is dict:#normal case
                for r in c[1][1]['rows']:
                    r['doc'] = makePrice(r['doc'])
                    makeOption(r, select, td_found[0])
                    r['doc'] = cleanDoc(r['doc'])
                    json.update({r['doc']['_id']:r['doc']})
            else: # multiple components
                for el in c[1][1]:
                    if el[0]:
                        option_group = etree.Element('optgroup')
                        option_group.set('label', el[1][0])
                        for r in el[1][1]['rows']:
                            r['doc'] = makePrice(r['doc'])
                            makeOption(r, option_group, td_found[0])
                            r['doc'] = cleanDoc(r['doc'])
                            json.update({r['doc']['_id']:r['doc']})
                        select.append(option_group)
            td_found[0].append(select)
    template.middle.find('script').text +='var choices=' + simplejson.dumps(json) + ';'

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
                                   .addCallback(lambda res: ("mother",res)))

    mother = [d for d in docs if isMother(d)][0]
    mother_cats = getCatalogsKey(mother)

    defs.append(couch.openView(designID,
                               'catalogs',
                               include_docs=True,
                               key=mother_to_proc_mapping[tuple(mother_cats)]).addCallback(lambda res: ("proc",res)))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=geforce)
                                    .addCallback(lambda res: ("GeForce",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=radeon)
                                    .addCallback(lambda res: ("Radeon",res))])
                .addCallback(lambda res: ("video",res)))

    defs.append(couch.openView(designID,
                               'catalogs',include_docs=True, key=ddr3).addCallback(lambda res: ("ram",res)))
    defs.append(couch.openView(designID,
                               'catalogs',include_docs=True, key=satas).addCallback(lambda res: ("hdd",res)))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=cases_400_650)
                                    .addCallback(lambda res: (u"Корпусы 400-650 Вт",res)),
                                   couch.openView(designID,
                                                  'catalogs',include_docs=True, key=cases_exclusive)
                                    .addCallback(lambda res: (u"Эксклюзивные корпусы",res))])
                .addCallback(lambda res: ("case",res)))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=displays_19_20)
                                    .addCallback(lambda res: (u"Мониторы 29-20 дюймов",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=displays_22_26)
                                    .addCallback(lambda res: (u"Мониторы 22-26 дюймов",res))])
                .addCallback(lambda res: ("displ",res)))


    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrds_a4)
                                    .addCallback(lambda res: ("Клавиатуры A4Tech",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrds_acme)
                                    .addCallback(lambda res: ("Клавиатуры Acme",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrds_chikony)
                                    .addCallback(lambda res: ("Клавиатуры Chikony",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=kbrds_game)
                                    .addCallback(lambda res: ("Игровые Клавиатуры",res)),])
                .addCallback(lambda res: ("kbrd",res)))

    defs.append(defer.DeferredList([couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouses_a4)
                                    .addCallback(lambda res: ("Мыши A4Tech",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouses_game)
                                    .addCallback(lambda res: ("Игровые Мыши",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouses_acme)
                                    .addCallback(lambda res: ("Мыши Acme",res)),
                                    couch.openView(designID,
                                                   'catalogs',include_docs=True, key=mouses_genius)
                                    .addCallback(lambda res: ("Мыши Genius",res))])
                .addCallback(lambda res: ("mouse",res)))

    return defer.DeferredList(defs).addCallback(lambda choices: (result, choices)) #.addCallback(renderChoices, template, skin, model).addCallback(lambda x: result)

def computer(template, skin, request):
    name = unicode(unquote_plus(request.path.split('/')[-1]), 'utf-8')
    _models = [m for m in models if m['name'] == name]
    model = _models[0] if len(_models)>0 else models[0]
    keys = [c for c in getModelComponents(model) if c is not None]
    d = couch.listDoc(keys=keys,include_docs=True)
    d.addCallback(fillChoices)
    d.addCallback(renderComputer, template, skin, model)
    return d
