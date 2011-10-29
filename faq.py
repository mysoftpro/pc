# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from copy import deepcopy


def renderFaq(res, template,skin, request):
    faq = template.root().find('faq')
    for r in res['rows']:
        viewlet = deepcopy(faq.find('div'))
        viewlet.text = r['doc']['text']
        template.middle.append(viewlet)
    skin.top = template.top
    skin.middle = template.middle
    return skin.render()

def faq(template, skin, request):
    d = couch.openView(designID,'faq',include_docs=True,stale=False,
                       startkey=['1'],endkey=['z'], limit=20)
    d.addCallback(renderFaq, template, skin, request)
    return d
