# -*- coding: utf-8 -*-
from twisted.trial import unittest
from twisted.internet import defer, reactor
from pc import models


class TestSave(unittest.TestCase):

    def setUp(self):
        models.gChoices = {models.proc:[], models.video:[]}
        models.gChoices_flatten = {}

    def makeTestModel(self, items):
        return models.Model({'_id':'test_model',
                              'items':items})


    def test_findComponent(self):
        model = self.makeTestModel({models.proc:'test proc'})
        found = model.findComponent(models.proc)

        self.assertTrue(found['price'] == 10)
        self.assertTrue(found['_id'] == 'test proc')
        self.assertFalse(found['replaced'])

        models.gChoices_flatten = {'test proc':{'_id':'replaced proc', 'price':20}}
        found1 = model.findComponent(models.proc)

        self.assertTrue(found1['price'] == 20)
        self.assertTrue(found1['_id'] == 'replaced proc')
        self.assertTrue(found1['replaced'])


    def test_buildProcAndVideo(self):
        model = self.makeTestModel({models.proc:'test proc',
                                       models.video:'test video'})
        proc_video = model.buildProcAndVideo()
        self.assertTrue(proc_video['proc_catalog'] == 'no')
        self.assertTrue(proc_video['video_catalog'] == 'no')
