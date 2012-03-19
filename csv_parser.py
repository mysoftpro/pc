# -*- coding: utf-8 -*-
import csv
from pc.couch import couch, designID
from twisted.internet import defer, reactor
from pc.models import Course
# from cStringIO import StringIO


class MaximusItem(object):
    def __init__(self, columns):
        self.text = unicode(columns[1],'utf-8')
        self._id = 'max_'+str(columns[2]).replace(' ','')
        self.max_stock = int(str(columns[3]).replace('>',''))
        try:
            self.cust_price = float(str(columns[4]).replace(',',''))
        except:
            self.cust_price = 0
        self.deal_price = float(str(columns[5]).replace(',',''))
        self.usd_price = float(str(columns[6]).replace('$', '').replace(',',''))

    def sync(self):
        d = couch.openDoc(self._id)
        d.addCallback(self.update)
        d.addErrback(self.add)
        return d

    def update(self, doc):
        need_save = False
        for field in ('text','cust_price','deal_price','usd_price','max_stock'):
            value = getattr(self,field)
            if doc[field] != value:
                need_save = True
                doc[field] = value
        retval = None
        if need_save:
            retval = couch.saveDoc(doc)
        return retval

    def add(self, fail):
        return couch.saveDoc({'_id':self._id,
                              'text':self.text,
                              'cust_price':self.cust_price,
                              'deal_price':self.deal_price,
                              'usd_price':self.usd_price,
                              'max_stock':self.max_stock})
    @classmethod
    def makeGen(cls, _file):
        return csv.reader(_file)


def maximus():
    _file = open('maximus.csv')
    gen = MaximusItem.makeGen(_file)
    def syncOnce(res, generator, opened_file):
        try:
            item = generator.next()
            while not '$' in item[-2]:
                item = generator.next()
            d = MaximusItem(item).sync()
            d.addCallback(syncOnce, generator,_file)
            return d
        except:
            import traceback,sys
            print str(sys.exc_info()[0])
            print traceback.format_exc()
            opened_file.close()
    return syncOnce(None, gen, _file)





class Sohotem(MaximusItem):
    EUR_TO_US = 1.207767164
    def __init__(self, columns):
        self._id = 'soh_'+"".join(filter(lambda x: ord(x)<128, str(columns[2]).replace(' ','')))
        self.text = unicode(columns[3],'utf-8')
        self.soh_stock = int(str(columns[4]).replace('>',''))
        need_rur = False
        price = str(columns[5])
        if ',' in price:
            if '.' in price:
                price = price.replace(',','')
            else:
                price = price.replace(',','.')
        price = price.replace(' ','')
        need_rur = False
        if 'RUB' in price:
            need_rur = True
            price = price.replace('RUB','')
        need_eur = False
        if 'EUR' in price:
            need_eur = True
            price = price.replace('EUR','')
        self.usd_price = float(price)
        if need_rur:
            self.usd_price = self.usd_price/Course
        if need_eur:
            self.usd_price = self.usd_price*self.EUR_TO_US


    def update(self, doc):
        need_save = False
        for field in ('text','usd_price','soh_stock'):
            value = getattr(self,field)
            if doc[field] != value:
                need_save = True
                doc[field] = value
        retval = None
        if need_save:
            retval = couch.saveDoc(doc)
        return retval

    def add(self, fail):
        return couch.saveDoc({'_id':self._id,
                              'text':self.text,
                              'usd_price':self.usd_price,
                              'soh_stock':self.soh_stock})


    @classmethod
    def makeGen(cls, _file):
        return csv.reader(_file)



def soho():
    _file = open('/home/aganzha/pc/soho.csv')
    gen = MaximusItem.makeGen(_file)
    def syncOnce(res, generator, opened_file):
        try:
            item = generator.next()
            while not 'шт' in item[-1]:
                item = generator.next()
            d = Sohotem(item).sync()
            d.addCallback(syncOnce, generator,_file)
            return d
        except:
            import traceback,sys
            print str(sys.exc_info()[0])
            print traceback.format_exc()
            opened_file.close()
    return syncOnce(None, gen, _file)




    # d = couch.openView(designID, 'maximus_components', stale=False)
    # def delete(res):
    #     print len(res['rows'])
    #     for r in res['rows'][1:]:
    #         try:
    #             couch.deleteDoc(r['key'],r['value'])
    #         except:
    #             import traceback,sys
    #             print str(sys.exc_info()[0])
    #             print traceback.format_exc()
    # d.addCallback(delete)
    # return d
