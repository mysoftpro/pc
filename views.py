# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from twisted.internet import defer
from pc.models import userFactory

class PCView(object):
    def __init__(self, template,skin,request, name):
        self.template = template
        self.request = request
        self.skin = skin
        self.name = name

    def preRender(self):
        pass

    def render(self):
        self.preRender()
        self.skin.top = self.template.top
        self.skin.middle = self.template.middle
        return defer.succeed(self.skin.render())




class Cart(PCView):
    def preRender(self):
        user = userFactory(self.name)        
