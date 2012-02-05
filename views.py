# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from twisted.internet import defer
from pc.models import userFactory, noChoicesYet, fillChoices, Model, cleanDoc,\
    notes,UserForCredit,tablet as tablet_catalog
from pc.models import model_categories,mouse,kbrd,displ,soft,audio, network,video,\
    noComponentFactory,parts, parts_names,mother_to_proc_mapping,INSTALLING_PRICE,BUILD_PRICE,\
    DVD_PRICE,parts_aliases,Course, VideoCard, Psu, video as video_catalog, psu as power_catalog,\
    Tablet as TabletOb, makeNotePrice,Router,\
    routers as router_catalog
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
	self.request = request
	self.model = model
	self.icon = deepcopy(self.tree.find('model_icon').find('a'))
	self.container = container
	self.getSnippetDivs()

    def getSnippetDivs(self):
	self.model_snippet = deepcopy(self.tree.find('model'))
	divs = self.model_snippet.findall('div')
	self.model_div = divs[0]
	self.description_div = divs[1]


    def setModelLink(self):

	if not self.model.isPromo:
	    self.icon.set('href','/computer/'+self.model._id)
	else:
	    self.icon.set('href','/promotion/'+self.model.parent)

	link = self.model_div.find('.//a')
	link.text = self.model._id[0:-3]
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
		info.set('class', info.get('class')+ ' confirm_info')
		info.set('title',u'Проверено!')
	    else:
		info.set('class', info.get('class')+ ' ask_info')
		info.set('title',u'Ожидает проверки специалистом')
	else:
	    info.set('class', info.get('class')+ ' empty_info')

    def set_price(self):
    	price_span = self.model_div.find('.//span')
	price_span.set('id',self.model._id)
	total = self.model.total
	if self.model.ourPrice:
	    total = self.model.ourPrice
	price_span.text = unicode(total) + u' р'




    def fillModelDiv(self):
	if self.model.processing:
	    header = self.model_div.find('h2')
	    header.set('class', header.get('class')+ ' processing')



	self.fillInfo()
	self.setModelLink()

        self.set_price()

	# self.icon.find('img').set('src',self.getCaseIcon())
	self.setIcon()
	self.model_div.insert(0,self.icon)
	self.container.append(self.model_div)

    #will be overriden by subclasses
    def setIcon(self):
	self.icon.find('img').set('src',self.model.case.getComponentIcon())

    def renderComponent(self, component):
	li = etree.Element('li')
	try:
	    if component.text:
		li.text = component.text
	    else:
		li.text=''
	except:
	    li.text = u'ошибка'

	if not 'promo' in self.model:
	    strong = etree.Element('strong')
	    strong.text = unicode(component.makePrice())+ u' р'
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

	if self.author:
	    a = etree.Element('a')
	    a.text = u'переименовать'
	    a.set('href', '')
	    h3.append(a)


    def fillComponentsList(self):
	ul = etree.Element('ul')
	ul.set('class','description')

	for c in self.model.getComponents():
	    ul.append(self.renderComponent(c))

	self.description_div.append(ul)


    def fillExtra(self):
	if self.author and not self.model.processing:
	    extra = deepcopy(self.tree.find('cart_extra'))
	    for el in extra:
		if el.tag == 'a' and 'class' in el.attrib and 'pdf_link' in el.attrib['class']:
		    el.set('href', '/bill.pdf?id='+self.model._id)
                if el.tag == 'a' and 'class' in el.attrib and 'credit_link' in el.attrib['class']:
		    el.set('href', '/credit_form/'+self.model._id)
		self.description_div.append(el)



    def fillDescriptionDiv(self):
	self.fillComponentsList()

	h3 = self.description_div.find('h3')

	self.fillHeader(h3)

	self.fillExtra()

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


class SetInCart(ModelInCart):

    def fillExtra(self):
	if self.author and not self.model.processing:
	    extra = deepcopy(self.tree.find('cart_extra'))
	    for el in extra:
		# TODO has the exactly same method allready. refacotor!
                if el.tag == 'a' and 'class' in el.attrib and 'pdf_link' in el.attrib['class']:
		    el.set('href', '/bill.pdf?id='+self.model._id)
                if el.tag == 'a' and 'class' in el.attrib and 'credit_link' in el.attrib['class']:
		    el.set('href', '/credit_form/'+self.model._id)
		if el.text!=u'Проверить':
		    self.description_div.append(el)

    def getSnippetDivs(self):
	self.model_snippet = deepcopy(self.tree.find('set'))
	divs = self.model_snippet.findall('div')
	self.model_div = divs[0]
	self.description_div = divs[1]

    def setVideoLink(self):
        video_doc = self.model.getComponent(video_catalog)
        url = '/videocard/'+\
            quote_plus(video_doc.get('articul','').replace('\t',''))

	self.icon.set('href',url)

	link = self.model_div.find('.//a')
	link.text = self.model._id[0:-3]
	strong= etree.Element('strong')

	strong.text = self.model._id[-3:]
	link.append(strong)

	#TODO may be other sets will have another link!
	link.set('href',url)


    def setTabletLink(self):
        tablet_doc = self.model.getComponent(tablet_catalog)
        url = '/tablet/'+\
            tablet_doc.get('vendor','')+'_'+tablet_doc.get('model','')
        url = url.replace(' ','_')

	self.icon.set('href',url)

	link = self.model_div.find('.//a')
	link.text = self.model._id[0:-3]
	strong= etree.Element('strong')

	strong.text = self.model._id[-3:]
	link.append(strong)

	#TODO may be other sets will have another link!
	link.set('href',url)


    def setModelLink(self):        
        if self.model.getComponent(video) is not None:
            self.setVideoLink()
        elif self.model.getComponent(tablet_catalog) is not None:
            self.setTabletLink()
        

    def setIcon(self):	        
        self.icon.find('img').\
            set('src',
                self.model.getComponentForIcon().\
                    getComponentIcon())



class NotebookInCart(SetInCart):


    def set_price(self):
    	price_span = self.model_div.find('.//span')
	price_span.set('id',self.model._id)	
	price_span.text = unicode(makeNotePrice(self.model.components[0].component_doc)['price']) +\
            u' р'

    def setModelLink(self):
	url = '/notebook'
	self.icon.set('href',url)

	link = self.model_div.find('.//a')
	link.text = self.model._id[0:-3]
	strong= etree.Element('strong')

	strong.text = self.model._id[-3:]
	link.append(strong)
	link.set('href',url)



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
	return d


class Cart(PCView):
    title = u'Корзина'

    def fixCookies(self, user, total):
	if user.isValid(self.request):
	    pcCartTotal(self.request, user.user, total=total)

    def preRender(self):
	user_d = userFactory(self.name)
        # fix cart! remove it in march please =)
        total = {}
	user_d.addCallback(self.renderModels, total)
	user_d.addCallback(self.renderPromos, total)
	user_d.addCallback(self.renderNotes, total)
	user_d.addCallback(self.renderSets, total)
	user_d.addCallback(self.fixCookies, total)
	return user_d


    def getModelsDiv(self):
	return self.template.middle.xpath('//div[@id="models"]')[0]


    def renderModels(self, user, total):
	models_div = self.getModelsDiv()
        total.update({'models':0})
	for m in user.getUserModels():
            total['models']+=1
	    view = ModelInCart(self.request, m, self.tree,
			       models_div, user.isValid(self.request) and m.isAuthor(user))
	    view.render()
	cart_form = deepcopy(self.tree.find('cart_comment_form'))
	models_div.append(cart_form.find('div'))
	return user

    # TODO! it must be 1 method. and multiple classes for all types!!!!!!
    # may be use adaptors?????????????
    def renderPromos(self, user, total):
	models_div = self.getModelsDiv()
        total.update({'promos':0})
	for m in user.getUserPromos():
            total['promos']+=1
	    view = ModelInCart(self.request, m, self.tree,
			       models_div, user.isValid(self.request) and m.isAuthor(user))
	    view.render()
	return user


    def getNotesDiv(self):
	return self.tree.find('notebook').find('div')

    def getSetDiv(self):
	return self.tree.find('set').find('div')



    def renderNotes(self, user, total):
	models_div = self.getModelsDiv()
        total.update({'notebooks':0})
	for m in user.getUserNotebooks():
            total['notebooks']+=1
	    view = NotebookInCart(self.request, m, self.tree,
			       models_div, user.isValid(self.request) and m.isAuthor(user))
	    view.render()
	return user


    def renderSets(self, user, total):
	models_div = self.getModelsDiv()
        total.update({'sets':0})
	for m in user.getUserSets():
            total['sets']+=1
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

    def setModelLink(self):
	link = self.model_div.find('.//a')
	link.text = self.model.name
	link.set('href','/computer/'+self.model._id)
	self.icon.set('href','/computer/'+self.model._id)

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

    def __init__(self, *args, **kwargs):
	super(Computer, self).__init__(*args, **kwargs)
	# self.script = self.template.middle.find('script')
	# self.script.text = ''
	self.title = u'Изменение конфигурации компьютера'

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
	    if name not in [mouse,kbrd,displ,soft,audio, network,video,power_catalog]: return
	    no_doc = noComponentFactory(component_doc, name)
	    if len(rows)==0:
		rows.insert(0,{'id':no_doc['_id'], 'key':no_doc['_id'],'doc':no_doc})
	    else:
		if rows[0]['id']!=no_doc['_id']:
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

	    #zzz
	    descr = etree.Element('div')
	    descr.set('class','description')
	    descr.text = ''

	    manu = etree.Element('div')
	    manu.set('class','manu')
	    manu.text = ''


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
	# title = self.skin.root().xpath('//title')[0]
	self.title = u' Изменение конфигурации компьютера '+h2.text

    def postRender(self):
	self.skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 300px;')
	self.skin.root().xpath('//div[@id="middle"]')[0].set('class','midlle_computer')



class Index(PCView):
    title = u'Компьютерный магазин Билд. Компьютеры в любой конфигурации. Большой выбор процессоров, материнских плат и видеокарт.'
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
    title=u'Лучшие видеокарты NVidia GeForce и ATI Radeon для апгрейда'

    def renderChips(self, chips):

	container = self.template.middle.xpath('//div[@id="models"]')[0]

	vendors = set()
        
	for chipname in chips:
	    viewlet = deepcopy(self.template.root().find('chip'))
	    chip_div = etree.Element('div')
	    chip_div.set('class', 'chip')

	    chip_title = viewlet.xpath('//h2[@class="chipname"]')[0]
	    chip_title.text = u'Видеокарта '
	    br = etree.Element('br')
	    _name = chipname
	    if 'HD' in _name:
		_name = 'Radeon '+_name
	    else:
		_name = 'GeForce '+_name
	    br.tail = _name
	    chip_title.append(br)
	    chip_image = viewlet.xpath('//img[@class="video_image"]')[0]
	    chip_image.set('alt', _name)

	    chip_vendors = viewlet.xpath('//ul[@class="chipVendors"]')[0]

	    from pc.models import gChoices_flatten as choices

	    image_was_set = False
	    rate_was_set = False
	    for _id in chips[chipname]:
		if _id not in choices:
		    continue
		doc = choices[_id]
		video_card = VideoCard(doc, video)

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
	    if len(chip_vendors)>0:
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

    def groupChips(self, res):
	chips = {}
	for row in res['rows']:
	    _id = row['id']
	    chip = row['value']
	    if chip in chips:
		chips[chip].append(_id)
	    else:
		chips[chip] = [_id]
	return chips

    def preRender(self):
	d = couch.openView(designID,'video_articul',stale=False)
	d.addCallback(self.groupChips)
	d.addCallback(self.renderChips)
	return d


class VideocardView(PCView):


    def __init__(self, *args, **kwargs):
	super(VideocardView, self).__init__(*args, **kwargs)
	self.script = self.template.middle.find('script')
	self.script.text = ''
	self.title = u'Видеокарта'

    def installPSUS(self, peak_power):
	json_psus = {}
	from pc import models
	psus = models.gChoices[models.psu][0][1][1]
	appr_psus = []
	for row in psus['rows'][1:]:
	    doc = row['doc']
	    if 'power' not in doc:continue
	    if doc['power']>=peak_power:
		psu = Psu(doc)
		appr_psus.append(psu)


	psu_list = self.template.middle.xpath('//ul')[0]
	for psu in sorted(appr_psus, lambda p1,p2: p1.makePrice()-p2.makePrice()):
	    json_psus[psu._id] = {'_id':psu._id,'name':psu.text,'price':psu.makePrice()}
	    li = etree.Element('li')
	    li.set('id', psu._id)

	    em = etree.Element('em')
	    em.text = psu.text.replace(u'Блок питания', '')

	    strong = etree.Element('strong')
	    strong.text = unicode(psu.makePrice())+u' р.'


	    span = etree.Element('span')
	    span.set('class','videoadd')
	    span.text = u'добавить к заказу'

	    li.append(em)
	    li.append(strong)
	    li.append(span)

	    psu_list.append(li)
	self.script.text += 'var psus='+simplejson.dumps(json_psus)+';'

    def fillNoCard(self):
        self.template.middle.xpath('//div[@id="maparams"]')[0].text = \
            u"""Здесь должна быть видеокарта, но сейчас ее нет в наличии. Пожалуйста, перейдите 
                на пункт "Видеокарты" в меню, чтобы посмотреть все видеокарты которые продаются у нас.
             """
        top = self.template.top.xpath('//div[@id="video_top"]')[0]
        top.getparent().remove(top)
        right = self.template.middle.xpath('//div[@id="videoimage"]')[0]
        right.getparent().remove(right)

    def renderCard(self, tuple_res):
	res = tuple_res[0]
	user = tuple_res[1]
	if len(res['rows'])==0:
	    self.force_no_resource = True            
            self.fillNoCard()
	    return
	res = res['rows'][0]

	from pc import models
	if not res['id'] in models.gChoices_flatten:
	    self.force_no_resource = True
            self.fillNoCard()
	    return
	card = VideoCard(models.gChoices_flatten[res['id']])
	self.title = card.text
        self.template.top.find('h1').text = card.text
	maparams = self.template.middle.xpath('//div[@id="maparams"]')[0]

	for el in html.fragments_fromstring(card.marketParams):
	    if type(el) is str or type(el) is unicode: break
	    maparams.append(el)
	if card.youtube:
	    d = etree.Element('div')
	    d.set('id','youtube')
	    for el in html.fragments_fromstring(card.youtube):
		if type(el) is str or type(el) is unicode: break
		d.append(el)
	    maparams.append(d)
	videoimage = self.template.middle.xpath('//div[@id="videoimage"]')[0].find('img')
	videoimage.set('alt', card.description.get('name', ''))
	videoimage.set('src', card.getComponentIcon())

	ol = self.template.top.xpath('.//div[@id="cart_to_computer"]')[0].find('ol')
	dump = simplejson.dumps({'video':card._id})
	for li in ol:
	    a = li.find('a')
	    a.set('href',a.get('href')+dump)

	if user is not None and 'models' in user:
	    for m in user['models']:
		li = etree.Element('li')
		a = etree.Element('a')
		a.text = m
		a.set('href','/computer/'+m+'?data='+dump)
		li.append(a)
		ol.append(li)

	videocons = self.template.middle.xpath('//span[@id="videocons"]')[0]
	videocons.text = str(card.power) +u' Вт'

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
	try:
	    dual = "SLI"
	    if 'HD' in card.chip:
	       dual="Crossfire"
	    self.template.middle.xpath('.//span[@id="mvideodual"]')[0].text=dual
	except:
	    pass
	self.script.text += 'var _id="'+card._id+'";var price='+str(card.makePrice())+';'
	self.script.text += 'var video_catalog='+video_catalog+';var power_catalog='+power_catalog+';'

    def prepareCardsAndUser(self, lires):
	cards = lires[0][1]
	user = None
	if lires[1][0]:
	    user = lires[1][1]
	return (cards,user)

    def preRender(self):
	""" here the name is articul. or doc['_id'] with replaced _new replaced by _
	(see hid property and articul.map.js)"""
	d = couch.openView(designID, 'video_articul', key=unquote_plus(self.name), stale=False)
	retval = d
	if self.request.getCookie('pc_cart') is not None:
	    d1 = couch.openDoc(self.request.getCookie('pc_user'))
	    li = defer.DeferredList((d,d1))
	    li.addCallback(self.prepareCardsAndUser)
	    li.addCallback(self.renderCard)
            retval = li
	else:
	    d.addCallback(lambda res:(res,None))
	    d.addCallback(self.renderCard)
	return retval

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
	d = couch.openView(designID, 'video_articul',
			   include_docs=True, key=unquote_plus(art), stale=False)
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
	d = couch.openView(designID, 'video_articul', include_docs=True, key=unquote_plus(art), stale=False)
	d.addCallback(self.getSpecs, request)
	return NOT_DONE_YET


def getNoteBookName(doc):

    if 'nname' in doc:
	return doc['nname']

    found = re.findall('[sSuU]+([a-zA-Z0-9 ]+)[ ][0-9\,\.0-9"]+[ ]',doc['text'])
    _text = None
    if len(found)>0:
	_text = found[0].strip()
	# doc['nname'] =_text
	# couch.saveDoc(doc)
    else:
	_text = doc['text'][0:doc['text'].index('"')]
	_text = _text.replace(u'Ноутбук ASUS','').replace(u'Ноутбук Asus','')
    return _text


def getNoteDispl(doc):
    if 'ndispl' in doc:
	return doc['ndispl']
    retval = ''
    found =re.findall('[sSuU]+[a-zA-Z0-9 ]+[ ]([0-9\,\.0-9"]+)[ ]',doc['text'])
    if len(found)>0:
	retval = found[0]
	# doc['ndispl'] =retval
	# couch.saveDoc(doc)
    return retval

def getNotePerformance(doc):
    if 'nperformance' in doc:
	return doc['nperformance']
    retval = ""
    found = re.findall('[0-9\,\.0-9"]+[ FHD, ]+([^/]*[/]+[^/]*)',doc['text'])
    if len(found)>0:
	retval = found[0]
	# doc['nperformance'] =retval
	# couch.saveDoc(doc)
    return retval


class NoteBooks(PCView):
    def renderNotebooks(self, result):
	json_notebooks= {}
	for r in result['rows']:
	    doc = makeNotePrice(r['doc'])
	    note_div = deepcopy(self.template.root().find('notebook').find('div'))
	    note_div.set('class',doc['_id']+' note')


	    link = note_div.xpath("//div[@class='nname']")[0].find('a')
	    name = getNoteBookName(doc)
	    link.text = name
	    if 'ourdescription' in doc:
		link.set('href','/notebook/'+name)
	    else:
		link.set('name',name)

	    for d in self.template.middle.xpath("//div[@class='notebook_column']"):
		clone = deepcopy(note_div)
		sort_div = clone.xpath("//div[@class='nprice']")[0]
		if d.get('id') == "s_price":
		    sort_div.text = unicode(doc['price'])+u' р.'
		if d.get('id') == "s_size":
		    sort_div.text = getNoteDispl(doc)
		if d.get('id') == "s_size":
		    sort_div.text = getNoteDispl(doc)
		if d.get('id') == "s_performance":
		    sort_div.text = getNotePerformance(doc)
		d.append(clone)

	    for token in ['id', 'flags','inCart',
			  'ordered','reserved','stock1', '_rev', 'warranty_type']:
                if token in doc:
                    doc.pop(token)
	    doc['catalogs'] = Model.getCatalogsKey(doc)
	    #TODO save all this shit found from re
	    json_notebooks.update({doc['_id']:doc})

	self.template.middle.find('script').text = 'var notebooks=' + simplejson.dumps(json_notebooks)

    title= u'Ноутбуки Asus'
    def preRender(self):
	from pc import models
	d = defer.Deferred()
	d.addCallback(lambda some:models.gChoices[notes])
	d.addCallback(self.renderNotebooks)
	d.callback(None)
	return d


letter_pat = re.compile('[a-zA-Z_]*')

class CreditForm(PCView):

    def fillUploadedAttachments(self, user_id, attachments):
	"""
	     i have passport in template. here i have passport, passport1 ...
	     it need to install all passport`s and icrement name in template for passportn
	"""
	keys = sorted(attachments.keys())
	clean_keys = {}
	all_keys = {}
	for k in keys:
	    clean = re.match(letter_pat,k).group()
	    number = k[len(clean):]
	    if number == '':
		number = 0
	    _int = int(number)
	    if clean not in clean_keys:
		clean_keys[clean] = _int
	    if _int>clean_keys[clean]:
		clean_keys[clean] = _int
	    if clean not in all_keys:
		all_keys[clean] = [k]
	    else:
		all_keys[clean].append(k)
	# now in clean keys i have all keys followed by the max numbers
	# in all_keys i have a grouping of all keys
	for k in all_keys.keys():
	    new_number = clean_keys[k]+1
	    field = self.template.middle.xpath('.//input[@name="'+k+'"]')[0]
	    field.set('name', k+str(new_number))
	    links = all_keys[k]
	    for l in links:
		a = etree.Element('a')
		a.set('href','/image/'+user_id+'/'+attachments[l])
		a.set('target','_blank')
		a.set('class', 'uploaded_file')
		a.text = attachments[l]
		span = etree.Element('span')
		span.text= u'удалить'
		span.set('style', u'margin-left:5px;')
		span.set('id', l)
		a.append(span)
		field.addprevious(a)
		field.addprevious(etree.Element('br'))


    def fillSavedForm(self, user_id, stored_credit, parent_name):
	for k,v in stored_credit.items():
	    if k=='attachments':
		self.fillUploadedAttachments(user_id, v)
	    value = unicode(v)
	    field = self.template.middle.xpath('.//input[@name="'+k+'"]')
	    if len(field)>0:
		field[0].set('value',value)
	    else:
		field = self.template.middle.xpath('.//select[@name="'+k+'"]')
		if len(field)>0:
		    options = field[0].findall('option')
		    for o in options:
			if o.get('value') == value:
			    o.set('selected','selected')
			else:
			    if 'selected' in o.attrib:
				del o.attrib['selected']
        if self.name != parent_name:
            self.template.middle.xpath('.//input[@id="parent"]')[0].set('value',parent_name)
        else:
            self.template.middle.xpath('.//input[@id="parent"]')[0].set('value','')

    def renderCreditFormForUser(self, user_doc):
	if self.name is None:
	    self.name = UserForCredit.idle_name
	user = UserForCredit(user_doc)
	stored, name = user.getStoredCredit(self.name, self.request.getCookie('pc_key'))
	if stored:
	    self.fillSavedForm(user._id, stored, name)
	from pc.root import credit_tarifs
	script = self.template.top.find('script')
	script.text = 'var monthly='+simplejson.dumps(credit_tarifs)+';'
	script.text+='var order="";var summ="";var order_name="";'


    def renderCreditFormForModel(self, model_doc):
	model = Model(model_doc)
	self.template.top.xpath('.//span[@id="orderid"]')[0].text = unicode(model._id)
	self.template.top.xpath('.//span[@id="total"]')[0].text = unicode(model.total)

    def preRender(self):
	d = couch.openDoc(self.request.getCookie('pc_user'))
	d.addCallback(self.renderCreditFormForUser)
	if self.name is not None:
	    d1= couch.openDoc(self.name)
	    d1.addCallback(self.renderCreditFormForModel)
	else:
	    d1 = defer.Deferred()
	    d1.callback(None)
	return defer.DeferredList((d,d1))


class Tablets(PCView):
    title=u'Планшетные компьютеры c ОС Android'
    def renderTablets(self, res):
        parent = self.template.middle.xpath('//div[@id="models"]')[0]
        viewlet = self.tree.find('tablet')
        for r in res['rows']:
            tab = TabletOb(r['doc'])
            container = deepcopy(viewlet)
            chip_div = etree.Element('div')
	    chip_div.set('class', 'chip tablet')
            br = etree.Element('br')
            chip_title = container.xpath('//h2[@class="chipname"]')[0]
	    chip_title.text = u'Планшетный компьютер'
            br.tail = tab.vendor +' '+tab.model
            chip_title.append(br)
            
            container.xpath('//td[@class="t_screen"]')[0].text = tab.screen
            container.xpath('//td[@class="t_memory"]')[0].text = tab.memory
            container.xpath('//td[@class="t_flash"]')[0].text = tab.flash
            container.xpath('//td[@class="t_os"]')[0].text = tab.os
            container.xpath('//td[@class="t_resolution"]')[0].text = tab.resolution
            icon = tab.getComponentIcon(default=None)

            if icon is not None:
                image = container.xpath('//img')[0]
                image.set('src', icon)
            
            video_img = container.xpath('//div[@class="modelicon videoicon"]')[0]
            rate = tab.rank
            while rate>0:
                d = etree.Element('div')
                d.set('class', 'video_rate')
                video_img.append(d)
                rate-=1

            chip_vendors = container.xpath('//ul[@class="chipVendors"]')[0]
            ve = etree.Element('li')
            ve.set('id', tab._id)
            link = etree.Element('a')
            span = etree.Element('span')
            strong = etree.Element('strong')
            span.text = u'Подробней'
            strong.text = unicode(tab.makePrice())
            strong.tail = u' р'
            link.text = u'На страницу товара'
            href = '/tablet/'+tab.vendor+'_'+tab.model
            link.set('href',href.replace(' ','_'))
            ve.append(span)
            ve.append(strong)
            ve.append(link)
            chip_vendors.append(ve)
            
            for el in container:
                chip_div.append(el)
            parent.append(chip_div)

    def preRender(self):
        from pc import models
        d = defer.Deferred()
    	d.addCallback(lambda some:models.gChoices[tablet_catalog])
	d.addCallback(self.renderTablets)
        d.callback(None)
        return d

class Tablet(PCView):
    
    def __init__(self, *args, **kwargs):
	super(Tablet, self).__init__(*args, **kwargs)
	self.script = self.template.middle.find('script')
	self.script.text = ''
        self.title = u'Планшетный компьютер'

    def renderTablet(self, res):
        if len(res['rows'])==0:
            self.force_no_resource=True
            return
        tab = TabletOb(res['rows'][0]['doc'])
        title = ' '+ tab.vendor+' '+tab.model +' '+tab.os
        self.title+=title
        self.template.top.xpath('//h1')[0].text+= title
        
        # self.template.top.xpath('//div[@id="tabletPrice"]')[0].text = u'Цена: '+unicode(doc['price'])+u' р'
        container = self.template.middle.xpath('.//div[@id="maparams"]')[0]
        if tab.youtube:
            for el in html.fragments_fromstring(tab.youtube):
                container.append(el)
            br = etree.Element('br')
            container.append(br)
        for el in html.fragments_fromstring(tab.description['comments']):
            if type(el) is unicode:
                if container[-1].tail is None:
                    container[-1].tail = ''
                container[-1].tail+=el
            else:
                container.append(el)

        routers = self.template.middle.xpath('//div[@id="videoimage"]')[0]
        for i in tab.description['imgs']:
            img = etree.Element('img')
            img.set('src','/image/'+tab._id+'/'+i+'.jpg')
            routers.insert(0,img)
        self.installRouters(routers)
        
        self.template.middle.find('script').text += 'var tablet_catalog='+tablet_catalog+';var _id="'\
            +tab._id+'";'


        price_table = self.template.middle.xpath('//table[@id="videoprice"]')[0]
	rows = price_table.findall('tr')
	for r in rows:
	    r[-1].text = unicode(tab.makePrice())+ u' р.'
	    first = r[0]
	    if first.text != u'Итого':
		first.find('div').text = tab.description.get('name', "")

        self.script.text += 'var _id="'+tab._id+'";var price='+str(tab.makePrice())+';'
	self.script.text += 'var tablet_catalog='+tablet_catalog+';var router_catalog='+router_catalog+';'



    def installRouters(self, routers_container):
	json_routers = {}
	from pc import models
        
        appr_routers = [Router(r['doc']) for r in models.gChoices[models.routers]['rows']]

        router_list = routers_container.find('ul')
	for router in sorted(appr_routers, lambda p1,p2: p1.makePrice()-p2.makePrice()):

            price = router.makePrice()
            if price<200:continue

	    json_routers[router._id] = {'_id':router._id,'name':router.text,'price':router.makePrice()}
	    li = etree.Element('li')
	    li.set('id', router._id)

	    em = etree.Element('em')
	    em.text = router.text.replace(u'Блок питания', '')

	    strong = etree.Element('strong')            
	    strong.text = unicode(price)+u' р.'


	    span = etree.Element('span')
	    span.set('class','videoadd')
	    span.text = u'добавить к заказу'

	    li.append(em)
	    li.append(strong)
	    li.append(span)
	    router_list.append(li)
	self.template.middle.find('script').text = 'var routers='+simplejson.dumps(json_routers)+';'



    def preRender(self):
        d = couch.openView(designID,'tablet_name',stale=False,include_docs=True,key=self.name)
        d.addCallback(self.renderTablet)
        return d


