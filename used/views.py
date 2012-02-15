# -*- coding: utf-8 -*-
from twisted.web.resource import Resource
from datetime import date
# http://localhost:5984/used/_design/used/_view/fetch?startkey=[%222012%22,%2202%22,%2202%22]&descending=true
from pc.views import PCView
from copy import deepcopy
from pc.used.couch import couch, designID
import simplejson
import re

def addSym(number):
    stri = str(number)
    if len(stri)==1:
        stri = "0"+stri
    return stri

def fetch(key=None):
    if key is None:
        today = date.today()
        key = [str(today.year),addSym(today.month),addSym(today.day)+'a']
    # endkey = ["2012", "02", "01"]
    return couch.openView(designID, 'fetch',startkey=key,descending=True, limit=50, include_docs=True)
    


class Used(PCView):    
    def renderAds(self, res):
        viewlet = self.tree.find('ad').find('div')
        container = self.template.middle.find('div')
        for r in res['rows']:
            doc = r['doc']
            match_phone = re.match('[0-9+\(\) -]*',doc['phone'])
            if match_phone is None:
                continue
            if doc['_id'] == 'a5cb8d7fc44c7bd5fd217709fa0252e6':
                print match_phone.group()
            real_phone = match_phone.group()
            view = deepcopy(viewlet)
            view.set('id',doc['_id'])
            view.xpath('//div[@class="ad_subject"]')[0].text = doc['subj']
            view.xpath('//div[@class="ad_body"]')[0].text = doc['text'].replace('_','')
            price = doc['price']
            if u'р' not in price:
                price += u' руб.'
            if u'Цена' not in price:
                price = u'Цена: '+ price
            view.xpath('//div[@class="ad_price"]')[0].text = price
            view.xpath('//div[@class="ad_date"]')[0].text = '.'.join(reversed(doc['date']))
            phone = ''
            
            for char in real_phone:
                phone+=str(ord(char))+':'
            view.xpath('//div[@class="ad_phone"]')[0].text = phone
            container.append(view)
                    
    
    def preRender(self):
        key = self.request.args.get('key',[None])[0]
        d = fetch(key)
        d.addCallback(self.renderAds)
        return d
