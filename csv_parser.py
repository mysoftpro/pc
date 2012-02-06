import csv
from pc.couch import couch, designID
from twisted.internet import defer
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

    def sync(self, some):
        d = couch.openDoc(self._id)
        d.addCallback(self.update)
        d.addErrback(self.add)
        

    def update(self, doc):
        for field in ('text','cust_price','deal_price','usd_price','max_stock'):
            doc[field] = getattr(self,field)
        return couch.saveDoc(doc)

    def add(self, fail):
        return couch.saveDoc({'_id':self._id,
                              'text':self.text,
                              'cust_price':self.cust_price,
                              'deal_price':self.deal_price,
                              'usd_price':self.usd_price,
                              'max_stock':self.max_stock})                
def maximus(_file):
    data = csv.reader(_file)
    items = []
    i = 0
    for row in data:
        i+=1
        if row[0] == '' and '$' in row[-2]:
            items.append(MaximusItem(row))
    d = defer.Deferred()
    d.callback(None)
    for item in items:
        d.addCallback(item.sync)
    return d

# if __name__ == '__main__':
#     f = open('maximus.csv')
#     maximus(f)
#     f.close()
#     print "done"
