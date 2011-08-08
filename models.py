# -*- coding: utf-8 -*-
from pc.couch import couch
from lxml import etree
from twisted.internet import defer
from string import Template

#               mother, proc, video, ram ,                    ide,   case,  displ, kbrd, mouse, sound, lan
models = [
    {'name':u"Локалхост",
     'items':   [19005, 18984, 18802, 17575,                   10661, 19165, 15252, 16499, 15998, None, None],
     'price':6500
     },
    {'name':u"Браузер",
     'items':   [19005, 18984, 18802, 17575,                   10661, 19165, 15252, 16499, 15998, None, None],
     'price':8500
     },
    {'name':u"Принтер",
     'items':   [19005, 18984, 18802, 17575,                   10661, 19165, 15252, 16499, 15998, None, None],
     'price':15200
     },
    {'name':u"Числодробилка",
     'items':   [19162, 18137, 18994, 17970,17970,17970,17970, 16991, 18219, 15606, 11383, 18185, None, None],
     'price':32000
     }
]



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


def render(components, m, image_i):
    # CACHE ALL MODELS HERE!!!
    m.update({'item_docs':components})
    template = Template(index_page_snippet)
    res = template.substitute(m, image=imgs[image_i]).encode('utf-8')
    return res

def index(content):
    i = 0
    defs = []
    for m in models:
	d = couch.listDoc(keys=[str(k) for k in m['items']],include_docs=True)
	d.addCallback(render, m, i)
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
