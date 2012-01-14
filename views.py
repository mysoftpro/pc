# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from twisted.internet import defer
from pc.models import userFactory, noChoicesYet, fillChoices, Model, cleanDoc, Model
from pc.models import model_categories,mouse,kbrd,displ,soft,audio, network,video,\
    noComponentFactory,parts, parts_names,mother_to_proc_mapping,INSTALLING_PRICE,BUILD_PRICE,DVD_PRICE,parts_aliases,Course, VideoCard, Psu, video as video_catalog, psu as power_catalog
from copy import deepcopy
from lxml import etree, html
from pc.common import forceCond, pcCartTotal
from urllib import unquote_plus, quote_plus
import simplejson
import re
from datetime import datetime,timedelta
from twisted.web.error import NoResource
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from pc.market import getMarket

class ModelInCart(object):
    def __init__(self, request, model, tree, container, author):
        self.author = author
        self.tree = tree
        self.model_snippet = deepcopy(self.tree.find('model'))
        self.request = request
        self.model = model
        self.icon = deepcopy(self.tree.find('model_icon').find('a'))
        self.container = container
        divs = self.model_snippet.findall('div')
        self.model_div = divs[0]
        self.description_div = divs[1]


    def setModelLink(self, link):

        link.text = self.model._id[:-3]
        strong= etree.Element('strong')

        strong.text = self.model._id[-3:]
        link.append(strong)

        if not self.model.isPromo:
            link.set('href','/computer/%s' % self.model._id)
        else:
            link.set('href','/promotion/%s' % self.model.parent)




    def fillInfo(self):
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



    def fillModelDiv(self):
        if self.model.processing:
            header = self.model_div.find('h2')
            header.set('class', header.get('class')+ ' processing')

        link = self.model_div.find('.//a')

        self.setModelLink(link)

        self.fillInfo()

        price_span = self.model_div.find('.//span')
        price_span.set('id',self.model._id)
        price_span.text = unicode(self.model.total) + u' р'

        if not self.model.isPromo:
            self.icon.set('href','/computer/'+self.model._id)
        else:
            self.icon.set('href','/promotion/'+self.model.parent)
            if self.model.ourPrice:
                price_span.text = unicode(self.model.ourPrice)+u' р.'
            else:
                price_span.text = u'24900 р.'
        # self.icon.find('img').set('src',self.getCaseIcon())
        self.setIcon()
        self.model_div.insert(0,self.icon)
        self.container.append(self.model_div)

    #will be overriden by subclasses
    def setIcon(self):
        self.icon.find('img').set('src',self.model.case.getComponentIcon())

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
        if component.old_code and not self.model.isPromo:
            a = etree.Element('a')
            a.text = u'Посмотреть старый компонент'
            a.set('href', '')
            a.set('class', 'showOldComponent')
            a.set('id', self.model._id+'_'+component.old_code)
            li.append(a)
        return li


    def fillHeader(self, h3):

        if self.model.name:
            span = etree.Element('span')
            span.set('class', 'customName')
            span.text = self.model.name
            h3.append(span)

        if self.model.title:
            span = etree.Element('span')
            span.set('class', 'customTitle')
            span.text = self.model.title
            h3.append(span)

        if not self.model.name and not self.model.title:
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


    def fillComponentsList(self):
        self.description_div.set('class','cart_description')
        ul = etree.Element('ul')
        ul.set('class','description')

        for c in self.model.getComponents():
            ul.append(self.renderComponent(c))

        self.description_div.append(ul)


    def fillDescriptionDiv(self):
        self.fillComponentsList()

        h3 = self.description_div.find('h3')
        self.fillHeader(h3)


        if self.author and not self.model.processing:
            extra = deepcopy(self.tree.find('cart_extra'))
            for el in extra:
                if el.tag == 'a' and 'class' in el.attrib and el.attrib['class']=='pdf_link':
                    el.set('href', '/bill.pdf?id='+self.model._id)
                self.description_div.append(el)

        comments_len = len(self.model.comments)
        if comments_len>0:
            last_index = comments_len-1
            i=0
            for comment in self.model.comments:
                comments = deepcopy(self.tree.find('cart_comment'))
                if not self.author and i==0:
                    comments.find('div').set('style', 'margin-top:40px')
                comments.xpath('//div[@class="faqauthor"]')[0].text = comment.author
                comment.date.reverse()
                comments.xpath('//div[@class="faqdate"]')[0].text = '.'.join(comment.date)
                comments.xpath('//div[@class="faqbody"]')[0].text = comment.body
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

        # self.icon.find('img').set('src',self.getNotebookIcon())
        self.setIcon()
        self.note.insert(0,self.icon)
        self.container.append(self.note)

    #will be overriden by subclasses
    def setIcon(self):
        self.icon.find('img').set('src',self.notebook.getComponentIcon())
        

class SetInCart(ModelInCart):

    def setModelLink(self, link):

        link.text = self.model._id[:-3]
        strong= etree.Element('strong')

        strong.text = self.model._id[-3:]
        link.append(strong)
        
        #TODO may be other sets will have another link!
        link.set('href', 
                 '/videocard/'+\
                     quote_plus(self.model.components[0].get('articul','').replace('\t','')))

    def setIcon(self):
        self.icon.find('img').set('src',self.model.components[0].getComponentIcon())


    def fillHeader(self, h3):
        h3.text = '.'.join(reversed(self.model.date))
        h3.set('style','margin-top:20px;')

class PCView(object):
    title = u'Компьютерный магазин Билд'

    def __init__(self, template,skin,request, name):
        self.template = template
        self.request = request
        self.skin = skin
        self.name = name
        self.tree = template.root()

    def preRender(self):
        pass

    def postRender(self):
        pass

    force_no_resource = False

    def noResource(self, fail=None):
        return NoResource().render(self.request)

    @forceCond(noChoicesYet, fillChoices)
    def render(self):
        d = self.preRender()
        if self.force_no_resource:
            return self.noResource()
        def _render(some):
            self.skin.top = self.template.top
            self.skin.middle = self.template.middle
            title = self.skin.root().xpath('//title')[0]
            title.text = self.title
            self.postRender()
            return self.skin.render()
        d.addCallback(_render)
        # d.addErrback(self.noResource)
        return d


class Cart(PCView):
    title = u'Корзина'
    def preRender(self):
        user_d = userFactory(self.name)
        user_d.addCallback(self.renderModels)
        user_d.addCallback(self.renderNotes)
        user_d.addCallback(self.renderSets)
        user_d.addCallback(lambda user:pcCartTotal(self.request, user.user))        
        return user_d


    def getModelsDiv(self):
        return self.template.middle.xpath('//div[@id="models"]')[0]


    def renderModels(self, user):
        models_div = self.getModelsDiv()
        for m in user.getUserModels():
            view = ModelInCart(self.request, m, self.tree,
                               models_div, user.isValid(self.request) and m.isAuthor(user))
            view.render()
        cart_form = deepcopy(self.tree.find('cart_comment_form'))
        models_div.append(cart_form.find('div'))
        return user


    def getNotesDiv(self):
        return self.tree.find('notebook').find('div')

    def getSetDiv(self):
        return self.tree.find('set').find('div')



    def renderNotes(self, user):
        models_div = self.getModelsDiv()
        clear_div = etree.Element('div')
        clear_div.set('style','clear:both')
        models_div.append(clear_div)
        note_div = self.getNotesDiv()
        icon = self.tree.find('model_icon').find('a')
        for n in user.getUserNotebooks():
            note_view = NotebookInCart(n,deepcopy(note_div),
                                            deepcopy(icon),
                                            models_div)
            note_view.render()
        return user


    def renderSets(self, user):
        models_div = self.getModelsDiv()
        for m in user.getUserSets():
            view = SetInCart(self.request, m, self.tree,
                               models_div, user.isValid(self.request) and m.isAuthor(user))
            view.render()
        return user



class ModelOnModels(ModelInCart):
    def fillInfo(self):
        pass
    def fillComponentsList(self):
        ul = etree.Element('ul')
        ul.set('class','description')
        ul.set('style','display:none')
        for c in self.model.getComponents():
            ul.append(self.renderComponent(c))
        self.description_div.append(ul)

    def fillHeader(self, h3):
        h3.text = self.model.title
        for el in html.fragments_fromstring(self.model.description):
            self.description_div.append(el)

    def setModelLink(self, link):
        link.text = self.model.name


    def postRender(self):
        self.model_div.set('id','m'+self.model._id)
        category = self.request.args.get('cat',[None])[0]
        if category in model_categories:
            if self.model._id in model_categories[category]:
                div = etree.Element('div')
                div.set('id', 'desc_'+self.model_div.get('id'))
                div.set('class', 'full_desc')
                if self.model.modeldesc:
                    div.text = self.model.modeldesc
                self.container.append(div)
                self.description_div.set('style','height:220px')
            else:
                self.model_div.set('style',"height:0;overflow:hidden")
                self.description_div.set('style',"height:0;overflow:hidden")




class Computers(Cart):
    title = u'Модели компьютеров'
    def renderComputers(self, res):
        models_div = self.getModelsDiv()
        models=  []
        for row in res['rows']:
            if row['doc'] is None:
                continue
            models.append(Model(row['doc']))
        json_prices = {}
        for model in sorted(models, lambda m1,m2: m2.order-m1.order):
            json_prices.update({model._id:model.cat_prices})
            json_prices[model._id]['total'] = model.total
            view = ModelOnModels(self.request, model, self.tree,
                                 models_div, False)
            view.render()
            view.postRender()
        self.template.middle.find('script').text = 'var prices=' + simplejson.dumps(json_prices) + ';'

    def preRender(self):
        d = couch.openView(designID,'models',include_docs=True,stale=False)
        d.addCallback(self.renderComputers)
        return d


no_component_added = False

class Computer(PCView):
    title=u'Изменение конфигурации компьютера'
    def preRender(self):
        d = couch.openDoc(self.name)
        d.addCallback(lambda m: Model(m))
        d.addCallback(self.renderComputer)
        return d

    def renderComputer(self, model):

        _uuid = ''
        author = ''
        parent = ''
        h2 =self.template.top.find('div').find('h2')
        # only original models have length

        if model.ours:
            h2.text = model.name
        else:
            h2.text = model._id[0:-3]
            strong = etree.Element('strong')
            strong.text = model._id[-3:]
            h2.append(strong)
            if model.name:
                span = etree.Element('span')
                span.text = model.name
                h2.append(span)
            _uuid = model._id
            author = model.author
            parent = model.parent

        if model.description:
            d = self.template.top.find('div').find('div')
            d.text = ''
            for el in html.fragments_fromstring(model.description):
                d.append(el)

        original_viewlet = self.template.root().find('componentviewlet')

        model_json = {}
        total = 0
        components_json = {}
        viewlets = []
        counted = {}

        def makeOption(row, price):
            option = etree.Element('option')
            if 'font' in row['doc']['text']:
                row['doc']['text'] = re.sub('<font.*</font>', '',row['doc']['text'])
                row['doc'].update({'featured':True})
            option.text = row['doc']['text']

            option.text +=u' ' + unicode(price) + u' р'

            option.set('value',row['id'])
            return option

        def appendOptions(options, container):
            for o in sorted(options, lambda x,y: x[1]-y[1]):
                container.append(o[0])


        #refactor! whats the fucken doc here???
        def noComponent(name, component_doc, rows):
            #hack!
            if 'catalogs' in component_doc:
                pass
            else:
                try:
                    component_doc['catalogs'] = Model.getCatalogsKey(rows[0]['doc'])
                except:
                    pass
            if globals()['no_component_added']:return
            if name not in [mouse,kbrd,displ,soft,audio, network,video]: return
            no_doc = noComponentFactory(component_doc, name)
            rows.insert(0,{'id':no_doc['_id'], 'key':no_doc['_id'],'doc':no_doc})

        def addComponent(_options, _row, current_id):
            _price= Model.makePrice(_row['doc'])
            _option = makeOption(_row, _price)
            _options.append((_option, _price))
            if _row['id'] == current_id:
                _option.set('selected','selected')
            _cleaned_doc = cleanDoc(_row['doc'], _price)
            _id = _cleaned_doc['_id']
            if _id in counted:
                _cleaned_doc.update({'count':counted[_id]})
            components_json.update({_id:_cleaned_doc})


        def fillViewlet(_name, _doc):
            tr = viewlet.find("tr")
            tr.set('id',_name)
            body = viewlet.xpath("//td[@class='body']")[0]
            body.set('id',_doc['_id'])
            body.text = re.sub('<font.*</font>', '',_doc['text'])

            descr = etree.Element('div')
            descr.set('class','description')
            descr.text = ''

            manu = etree.Element('div')
            manu.set('class','manu')
            manu.text = ''

            # our = etree.Element('div')
            # our.set('class','our')
            # our.text = u'нет рекоммендаций'

            clear = etree.Element('div')
            clear.set('style','clear:both;')
            clear.text = ''
            descr.append(manu);
            # descr.append(our)
            descr.append(clear)
            return descr
        from pc.models import gChoices
        for name,code in model:
            component_doc = None
            count = 1
            if code is None:
                component_doc = noComponentFactory({}, name)
            else:

                if type(code) is list:
                    count = len(code)
                    code = code[0]
                    counted.update({code:count})

                component_doc = model.findComponent(name)

            if _uuid == '' and 'replaced' in component_doc:
                # no need 'replaced' alert' in original models
                component_doc.pop('replaced')

            viewlet = deepcopy(original_viewlet)
            descr = fillViewlet(name, component_doc)

            price = Model.makePrice(component_doc)

            total += price
            # print component_doc
            cleaned_doc = cleanDoc(component_doc, price)
            cleaned_doc['count'] = count

            model_json.update({cleaned_doc['_id']:cleaned_doc})
            viewlet.xpath('//td[@class="component_price"]')[0].text = unicode(price*count) + u' р'

            ch = gChoices[name]
            options = []
            if type(ch) is list:
                noComponent(name, cleaned_doc, ch[0][1][1]['rows'])
                for el in ch:
                    if el[0]:
                        option_group = etree.Element('optgroup')
                        option_group.set('label', el[1][0])
                        _options = []
                        for r in el[1][1]['rows']:
                            addComponent(_options, r, cleaned_doc['_id'])
                        appendOptions(_options, option_group)
                        options.append((option_group, 0))
            else:
                noComponent(name, cleaned_doc, ch['rows'])
                for row in ch['rows']:
                    addComponent(options, row, cleaned_doc['_id'])

            select = viewlet.xpath("//td[@class='component_select']")[0].find('select')
            appendOptions(options, select)
            viewlets.append((parts[name],viewlet,descr))


        components_container = self.template.middle.xpath('//table[@id="components"]')[0]
        description_container = self.template.middle.xpath('//div[@id="descriptions"]')[0]

        import pc.models
        pc.models.no_component_added=True

        for viewlet in sorted(viewlets, lambda x,y: x[0]-y[0]):
            components_container.append(viewlet[1].find('tr'))
            description_container.append(viewlet[2])
        processing = False
        if 'processing' in model and model['processing']:
            processing = True

        self.template.middle.find('script').text = u''.join(('var model=',simplejson.dumps(model_json),
                                                        ';var processing=',simplejson.dumps(processing),
                                                        ';var uuid=',simplejson.dumps(_uuid),
                                                        ';var author=',simplejson.dumps(author),
                                                        ';var parent=',simplejson.dumps(parent),
                                                        ';var total=',unicode(total),
                                                        ';var choices=',simplejson.dumps(components_json),
                                                        ';var parts_names=',simplejson.dumps(parts_names),
                                                        ';var mother_to_proc_mapping=',
                                                        simplejson.dumps(mother_to_proc_mapping),
                                                        ';var proc_to_mother_mapping=',
                                                        simplejson.dumps([(el[1],el[0]) for el in mother_to_proc_mapping]),
                                                        ';var installprice=',str(INSTALLING_PRICE),
                                                        ';var buildprice=',str(BUILD_PRICE),
                                                        ';var dvdprice=',str(DVD_PRICE),

                                                        ';var idvd=',simplejson.dumps(model.dvd),
                                                        ';var ibuilding=',simplejson.dumps(model.building),
                                                        ';var iinstalling=',simplejson.dumps(model.installing),
                                                        ';var Course=',str(Course),
                                                        ';var parts=',simplejson.dumps(parts_aliases)
                                                        ))
        title = self.skin.root().xpath('//title')[0]
        title.text = u' Изменение конфигурации компьютера '+h2.text

    def postRender(self):
        self.skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 300px;')
        self.skin.root().xpath('//div[@id="middle"]')[0].set('class','midlle_computer')



class Index(PCView):
    title = u'Компьютерный магащин Билд. Компьютеры в любой конфигурации. Большой выбор процессоров, материнских плат и видеокарт.'
    imgs = ['static/comp_icon_1.png',
        'static/comp_icon_2.png',
        'static/comp_icon_3.png',
        'static/comp_icon_4.png'
        ]

    @classmethod
    def lastUpdateTime(self):
        now = datetime.now()
        hour = now.hour+8
        retval = ''
        mo = str(now.month)
        if len(mo)<2:
            mo = "0"+mo
        da = str(now.day)
        if len(da)<2:
            da = "0"+da
        if hour>18:
            retval = '.'.join((da,mo,str(now.year))) +' 18:15'
        elif hour<9:
            delta = timedelta(days=-1)
            now = now + delta
            retval = '.'.join((da,mo,str(now.year))) +' 18:15'
        else:
            if now.minute<14:
                hour-=1
            retval = '.'.join((da,mo,str(now.year))) +\
                ' '+str(hour)+':15'
        return retval


    def renderIndex(self, result):
        models = sorted([Model(row['doc']) for row in result['rows']],
                        lambda x,y: x.order-y.order)
        div = self.template.middle.xpath('//div[@id="computers_container"]')[0]
        json_prices = {}
        json_procs_and_videos = {}
        i = 0
        for m in models:
            model_snippet = self.tree.find('model')
            snippet = deepcopy(model_snippet.find('div'))
            snippet.set('style',"background-image:url('" + self.imgs[i] + "')")
            a = snippet.find('.//a')
            a.set('href','/computer/%s' % m._id)
            a.text=m.name
            price_span = snippet.find('.//span')
            price_span.set('id',m._id)
            price_span.text = unicode(m.total) + u' р'
            json_procs_and_videos.update({m._id:m.buildProcAndVideo()})
            json_prices.update({m._id:m.cat_prices})
            json_prices[m._id]['total'] = m.total
            div.append(snippet)
            i+=1
            if i==len(self.imgs): i=0
        self.template.middle.find('script').text = 'var prices=' + \
            simplejson.dumps(json_prices) + ';'+\
            'var procs_videos=' + simplejson.dumps(json_procs_and_videos) + ';'
        last_update = self.template.middle.xpath('//span[@id="last_update"]')[0]
        last_update.text = self.lastUpdateTime()



    def preRender(self):
        d = couch.openView(designID,'models',include_docs=True,stale=False)
        d.addCallback(self.renderIndex)
        return d


class VideoCards(PCView):
    title=u'Лучшие видеокарты GeForce и Radeon для апгрейда'
        
    def renderChips(self, res):
        chips = {}
        vendors = set()
        for row in res['rows']:
            if row['key'] in chips:
                chips[row['key']].append(row['value'])
            else:
                chips[row['key']] = [row['value']]
        container = self.template.middle.xpath('//div[@id="models"]')[0]

        for chipname in chips:
            viewlet = deepcopy(self.template.root().find('chip'))
            chip_div = etree.Element('div')
            chip_div.set('class', 'chip')

            chip_name_div = viewlet.xpath('//div[@class="chipname"]')[0]
            chip_name_div.text = u'Видеокарта '
            br = etree.Element('br')
            br.tail = chipname
            chip_name_div.append(br)

            chip_vendors = viewlet.xpath('//ul[@class="chipVendors"]')[0]

            from pc.models import gChoices_flatten as choices
            price_is_good = True
            image_was_set = False
            rate_was_set = False
            for _id in chips[chipname]:
                if _id not in choices:
                    continue
                doc = choices[_id]
                video_card = VideoCard(doc, video)

                if not video_card.goodPrice():
                    price_is_good = False
                    continue
                if not image_was_set:
                    icon = video_card.getComponentIcon(default=None)
                    if icon is not None:
                        image = viewlet.xpath('//img')[0]
                        image.set('src', icon)
                        image_was_set = True
                if not rate_was_set:
                    video_img = viewlet.xpath('//div[@class="modelicon videoicon"]')[0]
                    rate = video_card.rate
                    while rate>0:
                        d = etree.Element('div')
                        d.set('class', 'video_rate')
                        video_img.append(d)
                        rate-=1
                    rate_was_set = True

                if not video_card.vendor in vendors:
                    vendors.add(video_card.vendor)

                viewlet.xpath('//td[@class="vcores"]')[0].text = unicode(video_card.cores)
                viewlet.xpath('//td[@class="power"]')[0].text = unicode(video_card.power) + u' Вт'
                viewlet.xpath('//td[@class="year"]')[0].text = unicode(video_card.year)
                viewlet.xpath('//td[@class="memory"]')[0].text = unicode(video_card.memory)
                viewlet.xpath('//td[@class="memory_ammo"]')[0].text = unicode(video_card.memory_ammo)
                ve = etree.Element('li')
                ve.set('id', video_card._id)
                link = etree.Element('a')
                span = etree.Element('span')
                strong = etree.Element('strong')
                span.text = video_card.vendor
                strong.text = unicode(video_card.makePrice())
                strong.tail = u' р'
                link.text = u'На страницу товара'
                link.set('href','/videocard/'+quote_plus(video_card.hid))
                ve.append(span)
                ve.append(strong)
                ve.append(link)
                chip_vendors.append(ve)
            if price_is_good and len(chip_vendors)>0:
                for el in viewlet:
                    chip_div.append(el)
                container.append(chip_div)
        self.template.middle.find('script').text = 'var vendors='+simplejson.dumps(list(vendors))+';'
        vendors_boxes = self.template.top.xpath('//table[@id="video_vendor_list"]')[0]
        row = etree.Element('tr')
        vendors_boxes.append(row)
        vendor_td = self.template.root().find('vendor_td').find('td')
        i = 0
        for v in vendors:
            if i==4:
                row = etree.Element('tr')
                vendors_boxes.append(row)
            td = deepcopy(vendor_td)
            inp = td.find('input')
            inp.set('id', v.replace(' ','_'))
            label = td.find('label')
            label.set('for',v.replace(' ','_'))
            label.text = v
            row.append(td)
            i+=1
    def preRender(self):
        d = couch.openView(designID,'video_chips',stale=False)
        d.addCallback(self.renderChips)
        return d


class VideocardView(PCView):

    title=u'Видеокарта'
    
    def __init__(self, *args, **kwargs):
        super(VideocardView, self).__init__(*args, **kwargs)
        self.script = self.template.middle.find('script')
        self.script.text = ''

    def installPSUS(self, peak_power):
        json_psus = {}
        from pc import models
        psus = models.gChoices[models.psu][0][1][1]
        appr_psus = []
        for row in psus['rows']:
            doc = row['doc']
            if 'power' not in doc:continue
            if doc['power']>=peak_power:
                psu = Psu(doc)                
                appr_psus.append(psu)
        
        psu_list = self.template.middle.xpath('//ul')[0]
        for psu in sorted(appr_psus, lambda p1,p2: p1.makePrice()-p2.makePrice()):
            json_psus[psu._id] = {'_id':psu._id,'name':psu.text,'price':psu.makePrice()}
            li = etree.Element('li')
            li.text = psu.text.replace(u'Блок питания', '')
            li.set('id', psu._id)
            strong = etree.Element('strong')
            strong.text = unicode(psu.makePrice())+u' р.'

            span = etree.Element('span')
            span.set('class','videoadd')
            span.text = u'добавить к заказу'
            li.append(strong)
            li.append(span)
            psu_list.append(li)
        self.script.text += 'var psus='+simplejson.dumps(json_psus)+';'
        


    def renderCard(self, res):

        if len(res['rows'])==0:
            self.force_no_resource = True
            return
        res = res['rows'][0]

        if 'doc' not in res:
            self.force_no_resource = True
            return

        card = VideoCard(res['doc'])
        self.template.top.find('h1').text = card.text
        maparams = self.template.middle.xpath('//div[@id="maparams"]')[0]
        for el in html.fragments_fromstring(card.marketParams):
            maparams.append(el)
        videoimage = self.template.middle.xpath('//div[@id="videoimage"]')[0].find('img')
        videoimage.set('alt', card.description.get('name', ''))
        videoimage.set('src', card.getComponentIcon())

        
        videocons = self.template.middle.xpath('//span[@id="videocons"]')[0]
        videocons.text = card.power +u' Вт'
        
        peak = int(card.power)+350
        rest = peak%50
        peak = peak-rest+50
        
        self.installPSUS(peak)

        videopeak = self.template.middle.xpath('//span[@id="videopeak"]')[0]
        videopeak.text = unicode(peak) +u' Вт'

        price_table = self.template.middle.xpath('//table[@id="videoprice"]')[0]
        rows = price_table.findall('tr')
        for r in rows:
            r[-1].text = unicode(card.makePrice())+ u' р.'
            first = r[0]
            if first.text != u'Итого':
                first.find('div').text = card.description.get('name', card.text)
        self.script.text += 'var _id="'+card._id+'";var price='+str(card.makePrice())+';'
        self.script.text += 'var video_catalog='+video_catalog+';var power_catalog='+power_catalog+';'
    
    def preRender(self):
        """ here the name is articul. or doc['_id'] with replaced _new replaced by _
        (see hid property and articul.map.js)"""
        d = couch.openView(designID, 'articul', include_docs=True, key=unquote_plus(self.name), stale=False)
        d.addCallback(self.renderCard)
        return d

class MarketForVideo(Resource):

    def fail(self, request):
        request.write('')
        request.finish()
        return ""


    def done(self, lires, request):
        for tu in lires:
            if tu[0]:
                for el in tu[1]:
                    request.write(etree.tostring(el))
        request.finish()


    def getMarketComments(self, res, request):
        if len(res['rows'])==0:
            return self.fail(request)
        row = res['rows'][0]
        if not 'doc' in row:
            return self.fail(request)
        card = VideoCard(row['doc'])
        d = getMarket(card)
        d.addCallback(self.done, request)
        return d

    def render_GET(self, request):
        art = request.args.get('art', [None])[0]
        if art is None:
            return self.fail(request)
        d = couch.openView(designID, 'articul', include_docs=True, key=unquote_plus(art), stale=False)
        d.addCallback(self.getMarketComments, request)
        return NOT_DONE_YET

class SpecsForVideo(Resource):
    def fail(self, request):
        request.write('')
        request.finish()
        return ""

    def getSpecs(self, res, request):
        if len(res['rows'])==0:
            return self.fail(request)
        row = res['rows'][0]
        if not 'doc' in row:
            return self.fail(request)
        card = VideoCard(row['doc'])
        request.write(card.marketParams.encode('utf-8'))
        request.finish()

    def render_GET(self, request):
        art = request.args.get('art', [None])[0]
        if art is None:
            return self.fail(request)
        d = couch.openView(designID, 'articul', include_docs=True, key=unquote_plus(art), stale=False)
        d.addCallback(self.getSpecs, request)
        return NOT_DONE_YET

