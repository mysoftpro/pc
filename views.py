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
    def prepare(self, user_ob):
        print "yaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        print user_ob
        print user_ob.user
        print user_ob.notebooks
        print user_ob.models
    def preRender(self):
        user_d = userFactory(self.name)
        user_d.addCallback(self.prepare)
