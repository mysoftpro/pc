from twisted.trial import unittest
from twisted.internet import defer, reactor
from pc import market, couch
from pc.models import VideoCard
from lxml import etree

class TestMarket(unittest.TestCase):

    def done(self, some):
        print "done man!"

    def cardResult(self, lires, card):
        print "thats was the cart " + card._id + "\n"
        print card.marketComments
        print card.marketReviews
        for r in lires:
            if not r[0]:
                print "comments failed"
            else:
                print "are the some comments?: "
                for el in r[1]:
                    print el.xpath('//div[@class="date"]')[0].text
                    print type(el.xpath('//div[@class="date"]')[0].text)
                    #tostring(el)#unicode(etree.tostring(el), 'utf-8').encode('utf-8')
                

    def checkComments(self, res):
        lis = []
        for r in res['rows']:
            if 'doc' not in r:
                print "no doooooooooooooooooc" + r['key']
            doc = r['doc']
            card = VideoCard(doc)
            if card.has('marketComments') and card.has('marketParams') and card.has('marketReviews'):
                pass
            else:
                if card.has('year'):
                    print "something wrong with with card. we sell it, but not all params are present"
                    print card._id
                continue

            li = market.getMarket(card)
            li.addCallback(self.cardResult, card)
            lis.append(li)
            break
        tot = defer.DeferredList(lis)
        tot.addCallback(self.done)
        return tot

    def test_getMarket(self):
        d = couch.couch.openView(couch.designID,'video_chips',stale=False, include_docs = True)
        d.addCallback(self.checkComments)
        return d