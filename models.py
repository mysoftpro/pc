# -*- coding: utf-8 -*-
from pc.couch import couch
from lxml import etree
from twisted.internet import defer
from string import Template
from urllib import quote_plus, unquote_plus

#               mother, proc, video, ram ,                    ide,   case,  displ, kbrd, mouse, sound, lan
models = [
    {'name':u"Локалхост",
     'items':   {'mother':'19005', 'proc':'18984', 'video':'18802', 'ram':['17575'],'ide':'10661', 'case':'19165', 'displ':'15252', 'kbrd':'16499', 'mouse':'15998', 'sound':None, 'lan':None},
     'price':6500
     },
    {'name':u"Браузер",
     'items':   {'mother':'19005', 'proc':'18984', 'video':'18802', 'ram':['17575'],'ide':'10661', 'case':'19165', 'displ':'15252', 'kbrd':'16499', 'mouse':'15998', 'sound':None, 'lan':None},
     'price':8500
     },
    {'name':u"Принтер",
     'items':   {'mother':'19005', 'proc':'18984', 'video':'18802', 'ram':['17575'],'ide':'10661', 'case':'19165', 'displ':'15252', 'kbrd':'16499', 'mouse':'15998', 'sound':None, 'lan':None},
     'price':15200
     },
    {'name':u"Числодробилка",
     'items':   {'mother':'19162', 'proc':'18137', 'video':'18994', 'ram':['17970','17970','17970','17970'],'ide':'16991', 'case':'18219', 'displ':'15606', 'kbrd':'11383', 'mouse':'18185', 'sound':None, 'lan':None},
     'price':32000
     }
]

def components(model):
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


model_page_snippet = u"""
<div>
          <div class="item">
            <div class="features" style="background-image:url('static/acer-aspire-ie-3450-desktop-pc-1.png');">
                <ul>
                  <li>Интелл</li>
                  <li>2 ядра</li>
                  <li>2 Гб RAM</li>
                  <li>1 Гб VRAM</li>
                  <li>500 Гб HDD</li>
                  <li>Производительность: 500</li>
                </ul>
              </div>
              <div style="clear:both;"></div>
              <div class="price label">6500р.</div>
              <div class="name label">Локалхост.</div>
          </div>
        </div>
"""

index_page_snippet = u"""
<div style="background-image:url('$image')" class="indexitem">
<h3><a href="/computer/$name">$name: </a><span class="usprice">$price руб</span></h3>
</div>
"""


imgs = ['static/acer-aspire-ie-3450-desktop-pc-1.png',
        'static/compaq-presario-sg3440il-desktop-pc1.png',
        'static/dell-studio-hybrid-desktop-pc1.png',
        'static/desktop-pc1.png'
        ]


# item = etree.Element("div", CLASS="item")
    # a = etree.Element("a", href="", )
    # img = etree.Element("div", CLASS="icon")
    # img.append(imgs[image_i])
    # a.append(img)
    # price = etree.Element("div", CLASS="price label")
    # price.text = unicode(m['price']) + u'р.'
    # name = etree.Element("div", CLASS="name label")
    # name.text = m['name']
    # a.append(price)
    # a.append(name)
    # item.append(a)
    # return etree.tostring(item,encoding='utf-8')


def renderIndex(components, m, image_i):
    # CACHE ALL MODELS HERE!!!
    m.update({'item_docs':components})
    template = Template(index_page_snippet)
    res = template.substitute(m, image=imgs[image_i]).encode('utf-8')
    return res

def index(content, request):
    i = 0
    defs = []
    for m in models:
        d = couch.listDoc(keys=[c for c in components(m)],include_docs=True)
        d.addCallback(renderIndex, m, i)
        defs.append(d)
        i+=1
        if i==len(imgs): i=0

    def _render(res, _content):
        html = []
        for el in res:
            if el[0]:
                html.append(el[1])
        template = Template(_content)
        res = template.substitute(models=''.join(html))
        return res
    d = defer.DeferredList(defs)
    d.addCallback(_render, content)
    return d




def renderComputer(components, content, model):
    subst = {}
    for r in components['rows']:
        if r['key'] is None: continue
        _id = r['id']
        doc = r['doc']
        subst.update({component_name(_id, model):doc['text'].encode('utf-8')})
    return Template(content).safe_substitute(subst)

def computer(content, request):
    name = unicode(unquote_plus(request.path.split('/')[-1]), 'utf-8')
    _models = [m for m in models if m['name'] == name]
    model = _models[0] if len(_models)>0 else models[0]
    d = couch.listDoc(keys=[c for c in components(model)],include_docs=True)
    d.addCallback(renderComputer, content, model)
    return d
