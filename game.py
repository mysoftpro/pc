# -*- coding: utf-8 -*-
from twisted.internet import defer
def gamePage(template, skin, request):
    skin.top = template.top
    skin.middle = template.middle
    skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 190px;')
    skin.root().xpath('//div[@id="middle"]')[0].set('class','midlle_how')
    d = defer.Deferred()
    d.addCallback(lambda some:skin.render())
    d.callback(None)
    return d
