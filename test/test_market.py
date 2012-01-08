from twisted.trial import unittest
from twisted.internet import defer, reactor
from pc import market, couch
from pc.models import VideoCard

class TestMarket(unittest.TestCase):

    def done(self, some):
        print "done man!"

    def cardResult(self, lires, doc):
        print "thats was the cart " + doc['_id']
        for r in lires:
            if not r[0]:
                print "comments failed"
            else:
                print "are the some comments?: " +str(r[1])


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
            print "go for market page"
            d = market.getMarket(card.marketComments)
            d1 = market.getMarket(card.marketReviews)
            li = defer.DeferredList((d,d1))
            li.addCallback(self.cardResult, doc)
            lis.append(li)
        tot = defer.DeferredList(lis)
        tot.addCallback(self.done)
        return tot

    def test_getMarket(self):
        d = couch.couch.openView(couch.designID,'video_chips',stale=False, include_docs = True)
        d.addCallback(self.checkComments)
        return d
