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
    current_record = None
    for r in res['rows']:
        # print 'parent' in r['doc']
        # if not 'parent' in r['doc']:
        faq_viewlet = deepcopy(template.root().find('faq').find('div'))
        # else:
        faq_viewlet.set('id',r['doc']['_id'])
        author = faq_viewlet.xpath('//div[@class="faqauthor"]')[0]
        if 'name' in r['doc']:
            author.text = r['doc']['name']
        else:
            author.text = r['doc']['author']
        _date = r['doc']['date']
        _date.reverse()
        faq_viewlet.xpath('//div[@class="faqdate"]')[0].text = u'.'.join(_date)
        faq_viewlet.xpath('//div[@class="faqbody"]')[0].text = r['doc']['txt']
        if not 'parent' in r['doc']:
            faqs.append(faq_viewlet)
            current_record = faq_viewlet
        else:
            faq_viewlet.set('class',faq_viewlet.get('class')+' fanswer')
            faq_viewlet.remove(faq_viewlet.xpath('//div[@class="faqlinks"]')[0])
            current_record.append(faq_viewlet)        
    skin.top = template.top
    skin.middle = template.middle
    return skin.render()

def faq(template, skin, request):
    d = couch.openView(designID,'faq',include_docs=True,stale=True,
                       startkey=['z'],endkey=['1'], descending=True,limit=20)
    d.addCallback(renderFaq, template, skin, request)
    return d


class StoreFaq(Resource):
    def finish(self, res, doc, request):
        # send_email('admin@buildpc.ru',
        #            u'Кто-то оставил сообщение',
        #            simplejson.dumps(doc),
        #            sender=u'Компьютерный магазин <inbox@buildpc.ru>')
        request.write(str(res['id']))
        request.finish()
    def storeNameOrEmail(self, user_doc, name=None, email=None):
        need_to_store = False
        if name is not None:
            if 'names' in user_doc:
                if name not in user_doc['names']:
                    user_doc['names'].append(name)
                    need_to_store = True
            else:
                user_doc['names'] = [name]
                need_to_store = True
        if email is not None:
            if 'emails' in user_doc:
                if email not in user_doc['emails']:
                    user_doc['emails'].append(email)
                    need_to_store = True
            else:
                user_doc['emails'] = [email]
                need_to_store = True
        d = None
        if need_to_store:
            d = couch.saveDoc(user_doc)
        return d
        

    def render_POST(self, request):
        txt = request.args.get('txt',[None])[0]        
        if txt is None:
            return "ok"
        doc = {'_id':base36.gen_id(),'txt':txt,'date':str(date.today()).split('-'),'type':'faq'}
        doc.update({'author':request.getCookie('pc_user')})
        email = request.args.get('email',[None])[0]
        if email is not None:
            doc.update({'email':email})
        name = request.args.get('name',[None])[0]
        if name is not None:
            doc.update({'name':name})            
        if name is not None or email is not None:
            u = couch.openDoc(request.getCookie('pc_user'))
            u.addCallback(self.storeNameOrEmail, unicode(name, 'utf-8'), email)
        parent = request.args.get('parent',[None])
        if parent[0] is not None:
            doc['parent'] = parent
        d = couch.saveDoc(doc)
        d.addCallback(self.finish, doc, request)
        return NOT_DONE_YET               
