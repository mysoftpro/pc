# -*- coding: utf-8 -*-
from twisted.trial import unittest
from twisted.internet import defer, reactor
from pc import models, couch
from pc.couch import couch, designID, sync as couch_sync

class TestVideo(unittest.TestCase):

    def setUp(self):
        models.gChoices = {models.proc:[], models.video:[]}
        models.gChoices_flatten = {}
        return couch_sync()

    def getChips(self, res):
        print res

    def test_Chips(self):
        d = couch.openView(designID,'vieo_chops')
        d.addCallback(self.getChips)
        return d
