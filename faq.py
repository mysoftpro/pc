# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from copy import deepcopy
from twisted.web.resource import Resource
from pc import base36
from datetime import datetime, date
from twisted.web.server import NOT_DONE_YET
from pc.mail import send_email
import simplejson
from twisted.internet import reactor, defer
from twisted.web.resource import IResource
from lxml import etree, html

class Faq(object):
    _id = 'faq'
    title = u'Вопросы пользователей'
    def __init__(self, template, skin, request):
        self.template = template
        self.skin = skin
        self.request = request

    def prepareQuery(self):
        limit = self.request.args.get('limit',['20'])[0]
        try:
            ilimit = int(limit)
        except:
            ilimit = 20
        startkey=['z']
        endkey=['0']
        tag = self.request.args.get('tag', [None])[0]
        key = self.request.args.get('key', [None])[0]

        if tag is not None:
            startkey.insert(0,tag)
            endkey.insert(0,tag)
            d = couch.openView(designID,'blogtags',include_docs=True,stale=True,
                               startkey=startkey,endkey=endkey,limit=ilimit,descending=True)
        else:
            if key is not None:
                startkey.insert(0,key)
                endkey.insert(0,key)
            d = couch.openView(designID,self._id,include_docs=True,stale=True,
                               startkey=startkey,endkey=endkey, descending=True,limit=ilimit)
        d.addCallback(self.render)
        return d

    def fillTheTop(self):
        viewlet = deepcopy(self.template.root().find(self._id+'top'))
        for el in viewlet:
            self.template.top.append(el)

    def render(self, res):
        self.fillTheTop()
        title = self.skin.root().xpath('//title')[0]
        title.text = self.title
        faqs = self.template.middle.find('div')
        current_record = None
        i = 0
        title_from_blog = self.title
        for r in res['rows']:
            i+=1
            faq_viewlet = deepcopy(self.template.root().find('faq').find('div'))
            if 'title' in r['doc']:
                title_from_blog = r['doc']['title']
                ti = faq_viewlet.xpath('//h3[@class="faqtitle"]')[0]
                ti.text = r['doc']['title']
                ti.set('style','display:block')
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
            tag_container = faq_viewlet.xpath('//div[@class="faqtags"]')[0]
            for tag in r['doc'].get('tags',[]):
                a = etree.Element('a')
                a.set('href','/blog?tag='+tag)
                a.text = tag
                tag_container.append(a)
            text_field = faq_viewlet.xpath('//div[@class="faqbody"]')[0]
            text_field.text = ''
            if r['doc']['type'] == 'blog' and 'parent' not in r['doc']:
                for el in html.fragments_fromstring(r['doc']['txt']):
                    _t = type(el)
                    if  _t is unicode or _t is str:
                        text_field.text += el
                    else:
                        text_field.append(el)
            else:
                text_field.text = r['doc']['txt']
            if not 'parent' in r['doc']:
                faqs.append(faq_viewlet)
                current_record = faq_viewlet
            else:
                faq_viewlet.set('class',faq_viewlet.get('class')+' fanswer')
                # this will remove the links from answers
                faq_viewlet.remove(faq_viewlet.xpath('//div[@class="faqlinks"]')[0])
                current_record.append(faq_viewlet)
        if i==1:
            title.text = title_from_blog
        self.skin.top = self.template.top
        self.skin.middle = self.template.middle
        return self.skin.render()


class Blog(Faq):
    _id = 'blog'
    title = u'Блог'
    def fillTheTop(self):
        super(Blog, self).fillTheTop()
        form = deepcopy(self.template.root().xpath('//div[@id="faq_top"]')[0])
        form.set('style','display:none')
        self.template.top.append(form)


def faq(template, skin, request):
    view = Faq(template,skin,request)
    splitted = request.path.split('/')
    if len(splitted)>1 and splitted[1] == 'blog':
        view = Blog(template,skin,request)
    return view.prepareQuery()


class StoreFaq(Resource):
    def finish(self, res, doc, request):
        # uncomment!!!
        send_email('inbox@buildpc.ru',
                   u'Кто-то оставил сообщение',
                   simplejson.dumps(doc),
                   sender=u'Компьютерный магазин <admin@buildpc.ru>')
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

    def _storeBlog(self, doc, request):
        d = couch.saveDoc(doc)
        d.addCallback(self.finish, doc, request)
        return d


    def storeBlog(self, doc, request):
        from pc.admin import portal,auth_wrapper
        # get it from /usr/lib/python2.6/dist-packages/twisted/web/_auth/wrapper.py  L 120
        authheader = request.getHeader('authorization')
        factory, respString = auth_wrapper._selectParseHeader(authheader)
        credentials = factory.decode(respString, request)
        credentials.method = 'GET'
        login = portal.login(credentials, None, IResource)
        login.addCallbacks(self._storeBlog(doc, request), lambda x: request.finish())
        return NOT_DONE_YET

    types = ['faq','blog']

    def render_POST(self, request):
        txt = request.args.get('txt',[None])[0]
        if txt is None:
            return "ok"
        doc = {'_id':base36.gen_id(),'txt':txt,'date':str(date.today()).split('-')}
        _type = request.args.get('type',[None])[0]
        if _type is None or _type not in self.types:
            _type = 'faq'
        doc.update({'type':_type})

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

        title = request.args.get('title',[None])[0]
        if title is not None:
            doc['title'] = title

        blog = request.args.get('blog', [None])[0]
        if blog is not None:
            return self.storeBlog(doc, request)
        d = couch.saveDoc(doc)
        d.addCallback(self.finish, doc, request)
        return NOT_DONE_YET
