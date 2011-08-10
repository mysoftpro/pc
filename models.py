# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from lxml import etree
from twisted.internet import defer
from string import Template
from urllib import quote_plus, unquote_plus


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
    # "LGA1155"
    (components, mothers,"17961"):[components, procs, "18027"],
    # "LGA1156"
    (components,mothers,"12854"):[components,procs,"18028"],
    # "LGA1366"
    (components,mothers,"18029"):[components,procs,"9422"],
    #"LGA775":
    (components,mothers,"7449"):[components,procs,"7451"],
    # "SOCKET AM2 3":
    (components,mothers,"7699"):[components,procs,"7700"]
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



# index_page_snippet = u"""
# <div style="background-image:url('$image')" class="indexitem">
# <h3><a href="/computer/$name">$name: </a><span class="usprice">$price руб</span></h3>
# </div>
# """


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




def renderComputer(subst_elements, content, model):
    subst = subst_elements[0]
    elements = subst_elements[1]
    for r in elements['rows']:
        if r['key'] is None: continue
        _id = r['id']
        doc = r['doc']
        subst.update({component_name(_id, model):doc['text'].encode('utf-8')})
    subst.update({'name':model['name'].encode('utf-8')})
    subst.update({'modifname':(u'Модификация (' + model['name'] + u')').encode('utf-8')})
    return Template(content).safe_substitute(subst)


from twisted.python import log
import sys

def pr(some):
    log.startLogging(sys.stdout)
    log.msg(some)
    return some


def renderChoices(choices, content, model):
    substs = {}
    for c in choices:
        if c[0]:
            token = c[1][0]
            options = []
            if type(c[1][1]) is dict:
                for r in c[1][1]['rows']:
                    options.append(r['doc']['text'].encode('utf-8'))
                substs.update({token:"<select><option>%s</option></select>" % "</option><option>".join(options)})
            else:
                for el in c[1][1]:
                    if el[0]:
                        for r in el[1]['rows']:
                            options.append(r['doc']['text'].encode('utf-8'))
                substs.update({token:"<select><option>%s</option></select>" % "</option><option>".join(options)})
    return substs


def fillChoices(result, content, model):
    docs = [r['doc'] for r in result['rows'] if r['key'] is not None]
    mother = [d for d in docs if isMother(d)][0]

    defs = []

    mother_cats = getCatalogsKey(mother)

    defs.append(couch.openView(designID, 'catalogs',include_docs=True, key=mother_cats).addCallback(lambda res: ("mothers",res)))

    defs.append(couch.openView(designID, 'catalogs',include_docs=True, key=mother_to_proc_mapping[tuple(mother_cats)]).addCallback(lambda res: ("procs",res)))

    defs.append(defer.DeferredList([couch.openView(designID, 'catalogs',include_docs=True, key=geforce),
                                    couch.openView(designID, 'catalogs',include_docs=True, key=radeon)]).addCallback(lambda res: ("videos",res)))

    defs.append(couch.openView(designID, 'catalogs',include_docs=True, key=ddr3).addCallback(lambda res: ("rams",res)))
    defs.append(couch.openView(designID, 'catalogs',include_docs=True, key=satas).addCallback(lambda res: ("hdds",res)))

    defs.append(defer.DeferredList([couch.openView(designID, 'catalogs',include_docs=True, key=cases_400_650),
                                   couch.openView(designID, 'catalogs',include_docs=True, key=cases_exclusive)]).addCallback(lambda res: ("cases",res)))

    defs.append(defer.DeferredList([couch.openView(designID, 'catalogs',include_docs=True, key=displays_19_20),
                                    couch.openView(designID, 'catalogs',include_docs=True, key=displays_22_26)]).addCallback(lambda res: ("displays",res)))


    defs.append(defer.DeferredList([couch.openView(designID, 'catalogs',include_docs=True, key=kbrds_a4),
                                    couch.openView(designID, 'catalogs',include_docs=True, key=kbrds_acme),
                                    couch.openView(designID, 'catalogs',include_docs=True, key=kbrds_chikony),
                                    couch.openView(designID, 'catalogs',include_docs=True, key=kbrds_game)]).addCallback(lambda res: ("kbrds",res)))

    defs.append(defer.DeferredList([couch.openView(designID, 'catalogs',include_docs=True, key=mouses_a4),
                                    couch.openView(designID, 'catalogs',include_docs=True, key=mouses_game),
                                    couch.openView(designID, 'catalogs',include_docs=True, key=mouses_acme),
                                    couch.openView(designID, 'catalogs',include_docs=True, key=mouses_genius)]).addCallback(lambda res: ("mouses",res)))


    return defer.DeferredList(defs).addCallback(renderChoices, content, model).addCallback(lambda su: (su,result))

def computer(tree, skin, request):
    name = unicode(unquote_plus(request.path.split('/')[-1]), 'utf-8')
    _models = [m for m in models if m['name'] == name]
    model = _models[0] if len(_models)>0 else models[0]

    d = couch.listDoc(keys=[c for c in getModelComponents(model)],include_docs=True)
    d.addCallback(fillChoices, content, model)
    d.addCallback(renderComputer, content, model)
    return d
