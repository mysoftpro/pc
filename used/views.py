# -*- coding: utf-8 -*-
from twisted.web.resource import Resource
from datetime import date
# http://localhost:5984/used/_design/used/_view/fetch?startkey=[%222012%22,%2202%22,%2202%22]&descending=true
from pc.views import PCView
from copy import deepcopy
from pc.used.couch import couch, designID
import simplejson
import re
from urllib import unquote_plus, quote_plus
from twisted.internet import defer
from lxml import etree

def addSym(number):
    stri = str(number)
    if len(stri)==1:
        stri = "0"+stri
    return stri


gWords = None


def installgWords(res):
    globals()['gWords'] = res
    return res





class Used(PCView):
    items_on_page = 20
    title = u'Бывшие в употреблении'
    tag = None
    skip = 0
    def renderAds(self, li_res):
        viewlet = self.tree.find('ad').find('div')
        container = self.template.middle.xpath('.//div[@id="faq"]')[0]
        # last_key = None
        res = li_res[0][1]
        for r in res['rows']:
            doc = r['doc']
            # last_key = r['key']
            match_phone = re.match('[0-9+\(\) -]*',doc['phone'])
            if match_phone is None:
                continue
            real_phone = match_phone.group()
            view = deepcopy(viewlet)
            view.set('id',doc['_id'])
            view.xpath('//h4')[0].text = doc['subj']\
                .replace(u'Продам','')\
                .replace(u'Куплю',' ')\
                .replace(u'|','')
            view.xpath('.//p')[0].text = doc['text'].replace('_','')
            price = doc['price']
            if u'р' not in price:
                price += u' руб.'
            if u'Цена' not in price:
                price = u'Цена: '+ price
            view.xpath('//div[@class="ad_price"]')[0].find('span').text = price
            view.xpath('//div[@class="ad_date"]')[0].text = '.'.join(reversed(doc['date']))
            phone = ''

            for char in real_phone:
                phone+=str(ord(char))+':'
            view.xpath('//div[@class="ad_phone"]')[0].text = phone
            container.append(view)
        pager_links = self.template.middle.xpath('div[@id="used_pager"]')[0].findall('a')
        next = pager_links[-1]

        
        next.set('href','?skip='+str(self.skip+self.items_on_page))
        
        if self.tag is not None:
            next.set('href',unicode(next.get('href'))+u'&tag='+self.tag)
        if self.skip > 0:
            previous_link = etree.Element('a')
            previous_link.set('class','btn span1')
            icon = etree.Element('i')
            icon.set('class','icon-arrow-left')                                    
            icon.tail = u'назад'
            previous_link.set('href','?skip='+str(self.skip-self.items_on_page))
            previous_link.append(icon)
            if self.tag is not None:
                previous_link.set('href',
                                  unicode(previous_link.get('href'))+u'&tag='+self.tag)
            pager_links[0].getparent().insert(0,previous_link)
        if len(res['rows'])<self.items_on_page:
            next.getparent().remove(next)

        tag_res = li_res[1][1]
        tag_container = self.template.middle.xpath('.//div[@id="used_tags"]')[0]
        for row in sorted(tag_res['rows'], lambda row1,row2:row2['value']-row1['value']):
            if row['value'] <10:break
            a = etree.Element('a')
            a.set('href','?tag='+row['key'])
            a.text = row['key']+'-'+str(row['value'])
            tag_container.append(a)


    def preRender(self):
        today = date.today()
        key = [str(today.year),addSym(today.month),addSym(today.day)+'a']
        skip = self.request.args.get('skip',[0])[0]
        try:
            self.skip = int(skip)
        except:
            pass
        stale = not bool(self.request.args.get('stale',[''])[0])
        if not stale:
            globals()['gWords'] = None
        tag = self.request.args.get('tag',[None])[0]
        d = None
        if tag is None:
            self.title+=u' компьютеры и комплектующие'
            d = couch.openView(designID, 'fetch',startkey=key,descending=True, limit=self.items_on_page,
                          include_docs=True, skip=self.skip, stale=stale)
        else:
            self.tag = unicode(tag, 'utf-8')
            self.title=u'Бывший в употреблении '+self.tag
            d = couch.openView(designID, 'words',
                               key=self.tag, reduce=False,
                               stale=not bool(stale),
                               include_docs=True,limit=self.items_on_page,skip=self.skip)
        if globals()['gWords'] is None:            
            d1 = couch.openView(designID, 'words',reduce=True, group=True, stale=stale)
            d1.addCallback(installgWords)
        else:
            d1= defer.Deferred()
            d1.addCallback(lambda some: globals()['gWords'])
            d1.callback(None)
        li = defer.DeferredList((d,d1))
        li.addCallback(self.renderAds)
        return li
