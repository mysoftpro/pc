# -*- coding: utf-8 -*-
from twisted.trial import unittest
from twisted.internet import defer, reactor
from pc import models, couch


class TestVideo(unittest.TestCase):
    
    def setUp(self):        
        # if not reactor.running:
        #     reactor.run()
        models.gChoices = {models.proc:[], models.video:[]}
        models.gChoices_flatten = {}


    def test_Amock(self):
        pass

    def getChips(self, res):
        print "yaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        print res

    def test_Chips(self):
        d = couch.couch.openView(couch.designID,'vieo_chops')
        d.addCallback(self.getChips)
