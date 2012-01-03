# -*- coding: utf-8 -*-
from twisted.trial import unittest
from pc import models
from twisted.internet import reactor

class TestModel(unittest.TestCase):
    def setUp(self):
        print "yaaaaaaaaaaaaaa"
    def test_buildProcAndVideo(self):
        model = models.Model({'_id':'test_model',
                              'items':{}})
reactor.run()
