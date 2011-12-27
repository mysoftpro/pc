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
        if 'description' in self.model.case and'imgs' in self.model.case['description']:
            retval = ''.join(("/image/",self.model.case['_id'],"/",
                              self.model.case['description']['imgs'][0],'.jpg'))
        if '/preview' in retval:
            splitted = retval.split('/preview')
            retval = splitted[0]+quote_plus('/preview'+splitted[1]).replace('.jpg', '')

        return retval


    def fillComponents(self, price_span):
        #here is the difference between orders and models!!!
        self.components = buildPrices(self.model, self.json_prices, price_span, self.this_is_cart)

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

        #here is the difference between orders and models!!!
        self.fillComponents(price_span)

        if self.model.promo:
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

    def fillDescriptionDiv(self):
        # description_div = divs[1]
        ul = etree.Element('ul')
        ul.set('class','description')
        for cfm in self.components:
            ul.append(cfm.render())
        self.description_div.append(ul)

        h3 = self.description_div.find('h3')
        if not self.this_is_cart:
            h3.text = self.model['title']
            for el in html.fragments_fromstring(self.model['description']):
                self.description_div.append(el)
            ul.set('style','display:none')
        else:
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
            #self.user is not None and\
                # self.model['author'] == self.user['_id'] and\
                # self.request.getCookie('pc_key') == self.user['pc_key']

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
        if not self.this_is_cart:
            self.model_div.set('id','m'+self.model._id)
            if self.category in model_categories:
                if self.model._id in model_categories[self.category]:
                    div = etree.Element('div')
                    div.set('id', 'desc_'+self.model_div.get('id'))
                    div.set('class', 'full_desc')
                    if 'modeldesc' in self.model:
                        div.text = self.model['modeldesc']
                    self.container.append(div)
                    self.description_div.set('style','height:220px')
                else:
                    self.model_div.set('style',"height:0;overflow:hidden")
                    self.description_div.set('style',"height:0;overflow:hidden")




class OrderInCart(ModelInCart):
    def __init__(self, request, order, tree, this_is_cart, json_prices, icon, container, user):
        self.user = user
        self.tree = tree
        self.model_snippet = deepcopy(self.tree.find('model'))
        self.request = request
        self.order = order
        self.model = self.order['model']
        self.this_is_cart = this_is_cart
        self.json_prices = json_prices
        self.icon = icon
        self.container = container
        self.components = []
        divs = self.model_snippet.findall('div')
        self.model_div = divs[0]
        self.description_div = divs[1]
        self.category = request.args.get('cat',[None])[0]

    def fillComponents(self, price_span):
        #hack. see find component
        self.model['this_order'] = self.order
        self.components = buildPrices(self.model, self.json_prices, price_span, self.this_is_cart)


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
        return user_d
 

    def getModelsDiv(self):
        return self.template.middle.xpath('//div[@id="models"]')[0]


    def renderModels(self, user):
        json_prices = {}
        models_div = self.getModelsDiv()
        total = 0
        for m in user.getUserModels():
            if m.isOrder():
                view = OrderInCart(self.request, m, self.tree,
                                   True,json_prices,
                                   deepcopy(self.tree.find('model_icon').find('a')),
                                   models_div, user)
            else:
                view = ModelInCart(self.request, m, self.tree,
                                      True,json_prices,
                                      deepcopy(self.tree.find('model_icon').find('a')),
                                      models_div, user)
            view.render()
            total +=1
        print "---("
        print total
