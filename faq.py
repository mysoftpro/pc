# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from copy import deepcopy
from twisted.web.resource import Resource
from pc import base36
from datetime import datetime, date
from twisted.web.server import NOT_DONE_YET
from pc.mail import send_email
import simplejson

def renderFaq(res, template,skin, request):
    
    faqs = template.middle.find('div')
    for r in res['rows']:
        faq_viewlet = deepcopy(template.root().find('faq'))
        faq_viewlet.xpath('//div[@class="faqauthor"]')[0].text = r['doc']['_id']
        _date = r['doc']['date']
        _date.reverse()
        faq_viewlet.xpath('//div[@class="faqdate"]')[0].text = u'.'.join(_date)
        faq_viewlet.xpath('//div[@class="faqbody"]')[0].text = r['doc']['txt']
        faqs.append(faq_viewlet)
    skin.top = template.top
    skin.middle = template.middle
    return skin.render()

def faq(template, skin, request):
    d = couch.openView(designID,'faq',include_docs=True,stale=False,
                       startkey=['0'],endkey=['z'], limit=20)
    d.addCallback(renderFaq, template, skin, request)
    return d


class StoreFaq(Resource):
    def finish(self, res, doc, request):
        send_email('admin@buildpc.ru',
                   u'Кто-то оставил сообщение',
                   simplejson.dumps(doc),
                   sender=u'Компьютерный магазин <inbox@buildpc.ru>')
        request.write(str(res['id']))
        request.finish()
    def render_POST(self, request):
        txt = request.args.get('txt',[None])[0]
        if txt is None:
            return "ok"
        doc = {'_id':base36.gen_id(),'txt':txt,'date':str(date.today()).split('-'),'type':'faq'}
        doc.update({'author':request.getCookie('pc_user')})
        email = request.args.get('email',[None])[0]
        if email is not None:
            doc.update({'email':email})
        d = couch.saveDoc(doc)
        d.addCallback(self.finish, doc, request)
        return NOT_DONE_YET               
