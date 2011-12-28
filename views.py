# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from twisted.internet import defer
from pc.models import userFactory, noChoicesYet, fillChoices
from pc.models import buildPrices, case, model_categories
from copy import deepcopy
from lxml import etree, html
from pc.common import forceCond
from urllib import unquote_plus, quote_plus


class ModelInCart(object):
    def __init__(self, request, model, tree, this_is_cart, json_prices, icon, container, user):
        self.user = user
        self.tree = tree
        self.model_snippet = deepcopy(self.tree.find('model'))
        self.request = request
        self.model = model
        self.this_is_cart = this_is_cart
        self.json_prices = json_prices
        self.icon = icon
        self.container = container
        self.components = []
        divs = self.model_snippet.findall('div')
        self.model_div = divs[0]
        self.description_div = divs[1]
        self.category = request.args.get('cat',[None])[0]


    def getCaseIcon(self):
        retval = "/static/icon.png"
        if self.model.case.description and'imgs' in self.model.case.description:
            retval = ''.join(("/image/",self.model.case._id,"/",
                              self.model.case.description['imgs'][0],'.jpg'))
        if '/preview' in retval:
            splitted = retval.split('/preview')
            retval = splitted[0]+quote_plus('/preview'+splitted[1]).replace('.jpg', '')

        return retval


    def fillModelDiv(self):
        if self.model.isProcessing():
            header = self.model_div.find('h2')
            header.set('class', header.get('class')+ ' processing')

        link = self.model_div.find('.//a')
        link.text = self.model._id[:-3]
        strong= etree.Element('strong')

        strong.text = self.model._id[-3:]
        link.append(strong)

        if not self.model.promo:
            link.set('href','/computer/%s' % self.model._id)
        else:
            link.set('href','/promotion/%s' % self.model.parent)

        info = self.model_div.xpath('//div[@class="info"]')[0]
        if self.model.checkRequired:
            if self.model.checkPerformed:
                info.set('class', info.get('class')+ ' ask_info')
                info.set('title',u'Ожидает проверки специалистом')
            else:
                info.set('class', info.get('class')+ ' confirm_info')
                info.set('title',u'Проверено!')
        else:
            info.set('class', info.get('class')+ ' empty_info')


        price_span = self.model_div.find('.//span')
        price_span.set('id',self.model._id)
        price_span.text = unicode(self.model.total) + u' р'

        if not self.model.promo:
            self.icon.set('href','/computer/'+self.model._id)
        else:
            self.icon.set('href','/promotion/'+self.model.parent)
            if self.model.ourPrice:
                price_span.text = unicode(self.model.ourPrice)+u' р.'
            else:
                price_span.text = u'24900 р.'
        self.icon.find('img').set('src',self.getCaseIcon())
        self.model_div.insert(0,self.icon)
        self.container.append(self.model_div)


    def renderComponent(self, component):
        li = etree.Element('li')
        if component.text:
            li.text = component.text
        else:
            li.text=''
        if not 'promo' in self.model:
            strong = etree.Element('strong')
            strong.text = unicode(self.model.getComponentPrice(component))+ u' р'
            li.append(strong)
        li.set('id',self.model._id+'_'+component._id)
        if component.old_code and not self.model.promo:
            a = etree.Element('a')
            a.text = u'Посмотреть старый компонент'
            a.set('href', '')
            a.set('class', 'showOldComponent')
            a.set('id', self.model._id+'_'+component.old_code)
            li.append(a)
        return li



    def fillDescriptionDiv(self):
        # description_div = divs[1]
        ul = etree.Element('ul')
        ul.set('class','description')

        for c in self.model.getComponents():
            ul.append(self.renderComponent(c))

        self.description_div.append(ul)

        h3 = self.description_div.find('h3')

        if 'name' in self.model:
            span = etree.Element('span')
            span.set('class', 'customName')
            span.text = self.model['name']
            h3.append(span)

        if 'title' in self.model:
            span = etree.Element('span')
            span.set('class', 'customTitle')
            span.text = self.model['title']
            h3.append(span)

        if not 'name' in self.model and not 'title' in self.model:
            span = etree.Element('span')
            span.set('class', 'customName')
            span.text = u'Пользовательская конфигурация'
            h3.append(span)

        _date = self.model.date
        _date.reverse()
        span = etree.Element('span')
        span.text = ('.').join(_date)
        h3.append(span)

        a = etree.Element('a')
        a.text = u'переименовать'
        a.set('href', '')
        h3.append(a)

        self.description_div.set('class','cart_description')

        this_user_is_author = self.user.isValid(self.request) and self.model.isAuthor(self.user)

        if this_user_is_author and not 'processing' in self.model:
            extra = deepcopy(self.tree.find('cart_extra'))
            for el in extra:
                if el.tag == 'a' and 'class' in el.attrib and el.attrib['class']=='pdf_link':
                    el.set('href', '/bill.pdf?id='+self.model._id)
                self.description_div.append(el)

        if 'comments' in self.model:
            last_index = len(self.model['comments'])-1
            i=0
            for comment in self.model['comments']:
                comments = deepcopy(self.tree.find('cart_comment'))
                if not this_user_is_author and i==0:
                    comments.find('div').set('style', 'margin-top:40px')
                comments.xpath('//div[@class="faqauthor"]')[0].text = comment['author']
                comment['date'].reverse()
                comments.xpath('//div[@class="faqdate"]')[0].text = '.'.join(comment['date'])
                comments.xpath('//div[@class="faqbody"]')[0].text = comment['body']
                links = comments.xpath('//div[@class="faqlinks"]')[0]
                if i!=last_index:
                    links.remove(links.find('a'))
                i+=1
                self.description_div.append(comments.find('div'))
        self.container.append(self.description_div)


    def render(self):
        self.fillModelDiv()
        self.fillDescriptionDiv()



class NotebookInCart(object):

    def __init__(self,notebook, note, icon, container):
        self.icon = icon
        self.notebook = notebook
        self.note = note
        self.container = container


    def getNotebookIcon(self):
        retval = "/static/icon.png"
        if self.notebook.description and'imgs' in self.notebook.description:
            retval = ''.join(("/image/",self.notebook._id,"/",
                              self.notebook.description['imgs'][0],'.jpg'))
        if '/preview' in retval:
            splitted = retval.split('/preview')
            retval = splitted[0]+quote_plus('/preview'+splitted[1]).replace('.jpg', '')

        return retval


    def render(self):
        note_name = self.note.xpath('//div[@class="cnname"]')[0]
        note_name.text = self.notebook.text
        note_name.set('id',self.notebook.key+'_'+self.notebook._id)

        link = self.note.xpath('//strong[@class="modellink"]')[0]
        link.text = self.notebook.key[:-3]
        strong = etree.Element('strong')
        strong.text = self.notebook.key[-3:]
        link.append(strong)
        price = self.notebook.makePrice()

        self.note.xpath('//span[@class="modelprice"]')[0].text = unicode(price) + u' р.'

        self.icon.find('img').set('src',self.getNotebookIcon())
        self.note.insert(0,self.icon)
        self.container.append(self.note)


class PCView(object):
    def __init__(self, template,skin,request, name):
        self.template = template
        self.request = request
        self.skin = skin
        self.name = name
        self.tree = template.root()

    def preRender(self):
        pass

    @forceCond(noChoicesYet, fillChoices)
    def render(self):
        d = self.preRender()
        def _render(some):
            self.skin.top = self.template.top
            self.skin.middle = self.template.middle
            return self.skin.render()
        d.addCallback(_render)
        return d


class Cart(PCView):

    def preRender(self):
        user_d = userFactory(self.name)
        user_d.addCallback(self.renderModels)
        user_d.addCallback(self.renderNotes)
        return user_d


    def getModelsDiv(self):
        return self.template.middle.xpath('//div[@id="models"]')[0]


    def renderModels(self, user):
        json_prices = {}
        models_div = self.getModelsDiv()
        total = 0
        icon = self.tree.find('model_icon').find('a')
        for m in user.getUserModels():
            view = ModelInCart(self.request, m, self.tree,
                               True,json_prices,
                               deepcopy(icon),
                               models_div, user)
            view.render()
            total +=1

        cart_form = deepcopy(self.tree.find('cart_comment_form'))
        models_div.append(cart_form.find('div'))
        return user


    def getNotesDiv(self):
        return self.tree.find('notebook').find('div')


    def renderNotes(self, user):
        # TODO! make model view as for ComponentForModelsPage!!!!!!!!
        models_div = self.getModelsDiv()
        clear_div = etree.Element('div')
        clear_div.set('style','clear:both')
        models_div.append(clear_div)
        note_div = self.getNotesDiv()
        icon = self.tree.find('model_icon').find('a')
        for n in user.getUserNotebooks():
            # note_view = NoteBookForCartPage(n,deepcopy(note_div),key,
            #                                 deepcopy(tree.find('model_icon').find('a')),
            #                                 container)
            note_view = NotebookInCart(n,deepcopy(note_div),
                                            deepcopy(icon),
                                            models_div)
            note_view.render()

        # if 'notebooks' in result and 'user_doc' in result:
        #     total_notes = []
        #     need_cleanup = False
        #     note_div = template.root().find('notebook').find('div')
        #     clear_div = etree.Element('div')
        #     clear_div.set('style','clear:both')
        #     container.append(clear_div)
        #     for n in result['notebooks']['rows']:
        #         if not 'doc' in n:
        #             need_cleanup = True
        #             continue
        #         if n['doc'] is None:
        #             need_cleanup = True
        #             continue
        #         keys = [(k,v) for k,v in result['user_doc']['notebooks'].items() if v == n['doc']['_id']]
        #         if len(keys) == 0:
        #             need_cleanup = True
        #             continue
        #         key = keys[0][0]
        #         note_view = NoteBookForCartPage(n,deepcopy(note_div),key,
        #                                         deepcopy(tree.find('model_icon').find('a')),
        #                                         container)
        #         note_view.render()
        #         total_notes.append(n['doc']['_id'])
