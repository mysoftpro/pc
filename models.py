# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from lxml import etree, html
from twisted.internet import defer
import simplejson
import re
from copy import deepcopy
from urllib import unquote_plus
from datetime import datetime,timedelta
from pc.mail import send_email
from random import randint
import re
from twisted.web.resource import Resource

BUILD_PRICE = 800
INSTALLING_PRICE=800
DVD_PRICE = 800
NOTE_MARGIN=1500

gWarning_sent = []

components = "7363"
perifery = "7365"


proc = "7399"
mother = "7388"

mother_1155 = [components, mother,"17961"]
mother_1156 = [components,mother,"12854"]
mother_1366 =[components,mother,"18029"]
mother_775 = [components,mother,"7449"]
mother_am23 = [components,mother,"7699"]
mother_fm1 = [components,mother,"19238"]

video = "7396"

geforce = [components,video,"7607"]
radeon = [components,video,"7613"]

ram = "7394"
ddr3 = [components, ram, "11576"]
ddr2 = [components, ram, "7711"]
so_dim = [components, ram,"16993"]

hdd = "7406"
satas = [components, hdd,"7673"]
ides = [components, hdd,"7564"]

case = "7383"
case_400_650 = [components,case,"7459"]
case_exclusive = [components,case, "10837"]

displ = "7384"
displ_19_20 = [components,displ,"7526"]
displ_22_26 = [components,displ,"13209"]


kbrd = "7387"
kbrd_a4 = [perifery,kbrd,"14092"]
kbrd_acme = [perifery,kbrd,"7593"]
kbrd_chikony = [perifery,kbrd,"17396"]
kbrd_game = [perifery,kbrd,"18450"]


mouse = "7390"
mouse_a4 = [perifery,mouse,"7603"]
mouse_genius = [perifery,mouse,"15844"]
mouse_acme = [perifery,mouse,"14320"]
mouse_game = [perifery,mouse,"7582"]

sound = "7413"
sound_internal = [components,sound,"8012"]

network = "7405"
lan = [network,"14710"]

proc_1155 = [components, proc, "18027"]
proc_1156 = [components,proc,"18028"]
proc_1366 = [components,proc,"9422"]
proc_775 = [components,proc,"7451"]
proc_am23 = [components,proc,"7700"]
proc_fm1 =  [components,proc,"19257"]

audio = "7389"
audio_20 = [perifery,audio, "7447"]
audio_21 = [perifery,audio, "7448"]
audio_51 = [perifery,audio, "7462"]

soft = "7369"
microsoft = "14570"
windows = [soft,microsoft,"14571"]
power = [components,"7416","7464"]



mother_to_proc_mapping= [(mother_1155,proc_1155),
			 (mother_1156,proc_1156),
			 (mother_1366,proc_1366),
			 (mother_775,proc_775),
			 (mother_am23,proc_am23),
			 (mother_fm1,proc_fm1)]


def walkOnChoices(name = None, _filter=None):
    choices = None
    if name is not None:
	choices =globals()['gChoices'][name]
    else:
	choices = (v for k,v in globals()['gChoices'].items())
    if _filter is None:
	_filter = lambda x: True

    if type(choices) is dict:
	for ch in choices['rows']:
	    if _filter(ch['doc']):
		yield ch['doc']
    else:
	for el in choices:
	    if el[0]:
		for ch in el[1][1]['rows']:
		    if _filter(ch['doc']):
			yield ch['doc']



def getCatalogsKey(doc):
    if 'catalogs' not in doc:
	return 'no'
    if type(doc['catalogs'][0]) is dict:
	cats = []
	for c in doc['catalogs']:
	    cats.append(str(c['id']))
	return cats
    return doc['catalogs']


def getModelComponents(model):
    for k,v in model['items'].items():
	if type(v) is list:
	    for el in v:
		yield el
	else:
	    yield v


def nameForCode(code,model):
    retval = None
    for _name,_code in model['items'].items():
	if type(_code) is list and code in _code:
	    retval = _name
	    break
	elif  code == _code:
	    retval = _name
	    break
    return retval



Margin=1.15
Course = 31.1

def makePrice(doc):
    if doc['price'] == 0:
	return 0
    course = Course
    if getCatalogsKey(doc) == windows:
	course = 1
    our_price = float(doc['price'])*Margin*course
    return int(round(our_price/10))*10


def cleanDoc(doc, price):
    new_doc = {}
    to_clean = ['id', 'text', '_attachments','description','flags','inCart',
		     'ordered','reserved','stock1', '_rev', 'warranty_type']
    if ('sli' in doc and 'crossfire' in doc and 'ramslots' not in doc and 'stock1' in doc) and \
	    (doc['sli']>0 or doc['crossfire']>0) and doc['stock1']<=1:
	to_clean.append('sli')
	to_clean.append('crossfire')
    for token in doc:
	if token in to_clean:
	    continue
	if token == 'catalogs':
	    new_doc.update({token:getCatalogsKey(doc)})
	else:
	    new_doc.update({token:doc[token]})
    new_doc['price'] = price
    return new_doc

imgs = ['static/comp_icon_1.png',
	'static/comp_icon_2.png',
	'static/comp_icon_3.png',
	'static/comp_icon_4.png'
	]



parts = {mother:0, proc:10, video:20, hdd:30, ram:40,
	 case:50, displ:90,
	 audio:100, soft:110,
	 kbrd:120, mouse:130, audio:140}

parts_names = {proc:u'Процессор', ram:u'Память',
	       video:u'Видеокарта', hdd:u'Жесткий диск', case:u'Корпус',
	       sound:u'Звуковая карта',
	       network:u'Сетевая карта',
	       mother:u'Материнская плата',displ:u'Монитор',
	       audio:u'Аудиосистема', kbrd:u'Клавиатура', mouse:u'Мышь',
	       soft:u'ОС'}


parts_aliases = {
    'ram':ram,
    'mother':mother,
    'proc':proc,
    'video':video,
    'kbrd':kbrd,
    'mouse':mouse,
    'audio':audio,
    'sound':sound,
    'hdd':hdd,
    'displ':displ,
    'network':network,
    'soft':soft,
    'case':case
    }

def noComponentFactory(_doc, name):
    no_name = 'no' + name
    no_doc = deepcopy(_doc)
    no_doc['_id'] = no_name
    no_doc['price'] = 0
    no_doc['text'] = parts_names[name] + u': нет'
    return no_doc

# TODO! than replace mother or video
# check slots! may be 2 video installed with sli or with crossfire!
def replaceComponent(code,model):
    original_price = model['original_prices'][code] if code in ['original_prices'] else 10
    name = nameForCode(code,model)
    def sameCatalog(doc):
	retval = True
	if mother==name:
	    retval = model['mother_catalogs'] == getCatalogsKey(doc)
	if proc==name:
	    retval = model['proc_catalogs'] == getCatalogsKey(doc)
	return retval
    choices = globals()['gChoices'][name]
    flatten = []
    if type(choices) is list:
	for el in choices:
	    if el[0]:
		for ch in el[1][1]['rows']:
		    if sameCatalog(ch['doc']):
			flatten.append(ch['doc'])
    else:
	for ch in choices['rows']:
	    if sameCatalog(ch['doc']):
		flatten.append(ch['doc'])
    mock_component = noComponentFactory({},name)
    mock_component['price'] = original_price
    mock_component['_id'] = code
    flatten.append(mock_component)
    flatten = sorted(flatten,lambda x,y: int(x['price'] - y['price']))
    keys = [doc['_id'] for doc in flatten]
    _length = len(keys)
    ind = keys.index(code)
    _next = ind+1
    if _next == _length:
	_next = ind-1
    next_el = deepcopy(flatten[_next])
    if 'ours' in model and code not in globals()['gWarning_sent']:
	globals()['gWarning_sent'].append(code)
	text = model['name'] + ' '+parts_names[name] + ': '+code
	send_email('admin@buildpc.ru',
		   u'В модели заменен компонент',
		   text,
		   sender=u'Компьютерный магазин <inbox@buildpc.ru>')
    return next_el

no_component_added = False

def renderComputer(model, template, skin):
    _name = ''
    _uuid = ''
    author = ''
    parent = ''
    h2 =template.top.find('div').find('h2')
    # only original models have length
    if 'ours' in model:
	_name= model['name']
    else:
	_name = model['_id']
	_uuid = model.pop('_id')
	author = model.pop('author')
	if 'parent' in model:
	    parent = model.pop('parent')

    h2.text = _name

    if 'description' in model:
	# try:
	    d = template.top.find('div').find('div')
	    d.text = ''
	    for el in html.fragments_fromstring(model['description']):
		d.append(el)
	# except:
	#     pass
    original_viewlet = template.root().find('componentviewlet')
    choices = globals()['gChoices']

    model_json = {}
    total = 0
    components_json = {}
    viewlets = []
    counted = {}

    def makeOption(row, price):
	# try:
	    option = etree.Element('option')
	    if 'font' in row['doc']['text']:
		row['doc']['text'] = re.sub('<font.*</font>', '',row['doc']['text'])
		row['doc'].update({'featured':True})
	    option.text = row['doc']['text']

	    option.text +=u' ' + unicode(price) + u' р'

	    option.set('value',row['id'])
	    return option
	# except:
	#     print row
    def appendOptions(options, container):
	for o in sorted(options, lambda x,y: x[1]-y[1]):
	    container.append(o[0])


    def noComponent(name, component_doc, rows):
	#hack!


	try:
	    component_doc['catalogs'] = getCatalogsKey(rows[0]['doc'])
	except:
	    pass
	if globals()['no_component_added']:return
	if name not in [mouse,kbrd,displ,soft,audio, network,video]: return
	no_doc = noComponentFactory(component_doc, name)
	rows.insert(0,{'id':no_doc['_id'], 'key':no_doc['_id'],'doc':no_doc})

    def addComponent(_options, _row, current_id):
	_price= makePrice(_row['doc'])
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

	our = etree.Element('div')
	our.set('class','our')
	our.text = u'нет рекоммендаций'

	clear = etree.Element('div')
	clear.set('style','clear:both;')
	clear.text = ''
	descr.append(manu);
	descr.append(our)
	descr.append(clear)
	return descr


    for name,code in model['items'].items():
	component_doc = None
	count = 1
	if code is None:
	    component_doc = noComponentFactory({}, name)
	else:

	    if type(code) is list:
		count = len(code)
		code = code[0]
		counted.update({code:count})

	    component_doc = findComponent(model,name)

	if _uuid == '' and 'replaced' in component_doc:
	    # no need 'replaced' alert' in original models
	    component_doc.pop('replaced')

	viewlet = deepcopy(original_viewlet)
	descr = fillViewlet(name, component_doc)

	price = makePrice(component_doc)

	total += price

	cleaned_doc = cleanDoc(component_doc, price)
	cleaned_doc['count'] = count
	model_json.update({cleaned_doc['_id']:cleaned_doc})
	viewlet.xpath('//td[@class="component_price"]')[0].text = unicode(price*count) + u' р'

	ch = choices[name]
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


    components_container = template.middle.xpath('//table[@id="components"]')[0]
    description_container = template.middle.xpath('//div[@id="descriptions"]')[0]

    globals()['no_component_added'] = True

    for viewlet in sorted(viewlets, lambda x,y: x[0]-y[0]):
	components_container.append(viewlet[1].find('tr'))
	description_container.append(viewlet[2])
    processing = False
    if 'processing' in model and model['processing']:
	processing = True
    template.middle.find('script').text = u''.join(('var model=',simplejson.dumps(model_json),
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

						    ';var idvd=',simplejson.dumps(model['dvd']),
						    ';var ibuilding=',simplejson.dumps(model['building']),
						    ';var iinstalling=',simplejson.dumps(model['installing']),
						    ';var Course=',str(Course),
						    ';var parts=',simplejson.dumps(parts_aliases)
						    ))
    title = skin.root().xpath('//title')[0]
    title.text = u' Изменение конфигурации компьютера '+_name
    skin.top = template.top
    skin.middle = template.middle
    skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 280px;')
    skin.root().xpath('//div[@id="middle"]')[0].set('class','midlle_computer')
    return skin.render()


from twisted.python import log
import sys

def pr(some):
    log.startLogging(sys.stdout)
    log.msg(some)
    return some



gChoices = None
gChoices_flatten = {}

font_pat_1 = '<font[^>]*>[^<]*</font>'
font_pat_2 = '<font[^>]*>'

def cleanFlattenChoice(doc):
    def _pop(name):
	if 'descriptions' in doc and name in doc['descriptions']:
	    doc['descriptions'].pop(name)
    _pop('img')
    _pop('name')
    _pop('comments')
    doc['text'] = re.sub(font_pat_1,'',doc['text'])
    doc['text'] = re.sub(font_pat_2,'',doc['text'])


def flatChoices(res):
    for name,choices in globals()['gChoices'].items():
	if type(choices) is list:
	    for el in choices:
		if el[0]:
		    for ch in el[1][1]['rows']:
			cleanFlattenChoice(ch['doc'])
			globals()['gChoices_flatten'][ch['doc']['_id']] = ch['doc']
	else:
	    for ch in choices['rows']:
		cleanFlattenChoice(ch['doc'])
		globals()['gChoices_flatten'][ch['doc']['_id']] = ch['doc']



def equipCases(result):
    exclusive_rows = power = power_index = None
    i=0
    for r in result:
	if r[1][0] == u"Эксклюзивные корпусы":
	    exclusive_rows = r[1][1]['rows']
	elif r[1][0] == u"БП":
	    power = r[1][1]
	    power_index = i
	i+=1
    chipest_power = sorted([row['doc'] for row in power['rows']],lambda x,y:int(x['price']-y['price']))[0]
    for r in exclusive_rows:
	r['doc']['price'] += chipest_power['price']
    result.pop(power_index)
    return result




def fillChoices():
    # docs = [r['doc'] for r in result['rows'] if r['key'] is not None]
    _gChoices = globals()['gChoices']
    if _gChoices is not None:
	d = defer.Deferred()
	d.addCallback(lambda x: _gChoices)
	d.callback(None)
	return d
    defs = []
    defs.append(defer.DeferredList([
		# couch.openView(designID,
		#                                  'catalogs',
		#                                  include_docs=True, key=mother_1366, stale=False)
		#                   .addCallback(lambda res: ("LGA1366",res)),
				    couch.openView(designID,
						   'catalogs',
						   include_docs=True, key=mother_1155, stale=False)
				    .addCallback(lambda res: ("LGA1155",res)),
				    couch.openView(designID,
						   'catalogs',
						   include_docs=True, key=mother_1156, stale=False)
				    .addCallback(lambda res: ("LGA1166",res)),
				    couch.openView(designID,
						   'catalogs',
						   include_docs=True, key=mother_775, stale=False)
				    .addCallback(lambda res: ("LGA775",res)),
				    couch.openView(designID,
						   'catalogs',
						   include_docs=True, key=mother_am23, stale=False)
				    .addCallback(lambda res: ("AM2 3",res)),
				    couch.openView(designID,
						   'catalogs',
						   include_docs=True, key=mother_fm1, stale=False)
				    .addCallback(lambda res: ("FM1",res))
				    ])
		.addCallback(lambda res: {mother:res}))


    defs.append(defer.DeferredList([couch.openView(designID,
						   "catalogs",
						   include_docs=True,key=proc_1155, stale=False)
				    .addCallback(lambda res:('LGA1155',res)),
				    couch.openView(designID,
						   'catalogs',
						   include_docs=True,key=proc_1156, stale=False)
						   .addCallback(lambda res:('LGA1156',res)),
				    # couch.openView(designID,
				    #              'catalogs',
				    #              include_docs=True,key=proc_1366, stale=False)
				    #              .addCallback(lambda res:('LGA1366',res)),
				    couch.openView(designID,
						   'catalogs',
						   include_docs=True,key=proc_am23, stale=False)
				    .addCallback(lambda res:('AM2 3',res)),
				    couch.openView(designID,
						   'catalogs',
						   include_docs=True,key=proc_775, stale=False)
						   .addCallback(lambda res:('LGA755',res)),
				    couch.openView(designID,
						   'catalogs',
						   include_docs=True, key=proc_fm1, stale=False)
				    .addCallback(lambda res: ("FM1",res))
				    ])

		.addCallback(lambda res: {proc:res}))

    defs.append(defer.DeferredList([couch.openView(designID,
						   'catalogs',include_docs=True, key=geforce, stale=False)
				    .addCallback(lambda res: (u"GeForce",res)),
				    couch.openView(designID,
						   'catalogs',include_docs=True, key=radeon, stale=False)
				    .addCallback(lambda res: (u"Radeon",res))])
		.addCallback(lambda res: {video:res}))

    defs.append(couch.openView(designID,
			       'catalogs',include_docs=True, key=ddr3, stale=False)
		.addCallback(lambda res: {ram:res}))
    defs.append(couch.openView(designID,
			       'catalogs',include_docs=True, key=satas, stale=False)
		.addCallback(lambda res: {hdd:res}))
    defs.append(couch.openView(designID,
			       'catalogs',include_docs=True, key=windows, stale=False)
		.addCallback(lambda res: {soft:res}))

    defs.append(defer.DeferredList([couch.openView(designID,
						   'catalogs',include_docs=True, key=case_400_650, stale=False)
				    .addCallback(lambda res: (u"Корпусы 400-650 Вт",res)),
				    couch.openView(designID,
						   'catalogs',include_docs=True, key=power, stale=False)
				    .addCallback(lambda res: (u"БП",res)),
				   couch.openView(designID,
						  'catalogs',include_docs=True, key=case_exclusive, stale=False)
				    .addCallback(lambda res: (u"Эксклюзивные корпусы",res))])
		.addCallback(equipCases)
		.addCallback(lambda res: {case:res}))

    defs.append(defer.DeferredList([couch.openView(designID,
						   'catalogs',include_docs=True, key=displ_19_20, stale=False)
				    .addCallback(lambda res: (u"Мониторы 19-20 дюймов",res)),
				    couch.openView(designID,
						   'catalogs',include_docs=True, key=displ_22_26, stale=False)
				    .addCallback(lambda res: (u"Мониторы 22-26 дюймов",res))])
		.addCallback(lambda res: {displ:res}))


    defs.append(defer.DeferredList([couch.openView(designID,
						   'catalogs',include_docs=True, key=kbrd_a4, stale=False)
				    .addCallback(lambda res: (u"Клавиатуры A4Tech",res)),
				    couch.openView(designID,
						   'catalogs',include_docs=True, key=kbrd_acme, stale=False)
				    .addCallback(lambda res: (u"Клавиатуры Acme",res)),
				    couch.openView(designID,
						   'catalogs',include_docs=True, key=kbrd_chikony, stale=False)
				    .addCallback(lambda res: (u"Клавиатуры Chikony",res)),
				    couch.openView(designID,
						   'catalogs',include_docs=True, key=kbrd_game, stale=False)
				    .addCallback(lambda res: (u"Игровые Клавиатуры",res)),])
		.addCallback(lambda res: {kbrd:res}))

    defs.append(defer.DeferredList([couch.openView(designID,
						   'catalogs',include_docs=True, key=mouse_a4, stale=False)
				    .addCallback(lambda res: (u"Мыши A4Tech",res)),
				    couch.openView(designID,
						   'catalogs',include_docs=True, key=mouse_game, stale=False)
				    .addCallback(lambda res: (u"Игровые Мыши",res)),
				    couch.openView(designID,
						   'catalogs',include_docs=True, key=mouse_acme, stale=False)
				    .addCallback(lambda res: (u"Мыши Acme",res)),
				    couch.openView(designID,
						   'catalogs',include_docs=True, key=mouse_genius, stale=False)
				    .addCallback(lambda res: (u"Мыши Genius",res))])
		.addCallback(lambda res: {mouse:res}))

    defs.append(defer.DeferredList([couch.openView(designID,
						   'catalogs',include_docs=True, key=audio_20, stale=False)
				    .addCallback(lambda res: (u"Аудио системы 2.0",res)),
				    couch.openView(designID,
						   'catalogs',include_docs=True, key=audio_21, stale=False)
				    .addCallback(lambda res: (u"Аудио системы 2.1",res)),
				    couch.openView(designID,
						   'catalogs',include_docs=True, key=audio_51, stale=False)
				    .addCallback(lambda res: (u"Аудио системы 5.1",res))])
		.addCallback(lambda res: {audio:res}))
    def makeDict(res):
	new_res = {}
	for el in res:
	    if el[0]:
		new_res.update(el[1])
	globals()['gChoices'] = new_res
	flatChoices(new_res)
	return globals()['gChoices']
    #TODO - this callback to the higher level
    return defer.DeferredList(defs).addCallback(makeDict)



def computer(template, skin, request):
    if globals()['gChoices'] is None:
	d = fillChoices()
	d.addCallback(lambda some: computer(template, skin, request))
	return d

    splitted = request.path.split('/')
    name = unicode(unquote_plus(splitted[-1]), 'utf-8')
    # hack! just show em ping!
    if len(name) == 0:
	name = 'ping'
    d = couch.openDoc(name)
    d.addCallback(renderComputer, template, skin)
    #d.addErrback(lambda x: couch.openDoc('cell').addCallback(renderComputer, template, skin))
    return d



model_categories = {'home':['storage','spline','shade'],
		    'work':['localhost','scroll','chart'],
		    'admin':['ping','cell','compiler'],
		    'game':['zoom','render','raytrace']}

model_categories_titles = {'home':u'Домашние компьютеры',
			   'work':u'Компьюетры для работы',
			   'admin':u'Компьютеры для айтишников',
			   'game':u'Игровые компьютеры'}

class ModelForModelsPage(object):
    def __init__(self, request, model, model_snippet, this_is_cart, json_prices, icon, container):
	self.model_snippet = model_snippet
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

    def fillModelDiv(self):
	if 'processing' in self.model and self.model['processing']:
	    header = self.model_div.find('h2')
	    header.set('class', header.get('class')+ ' processing')
	a = self.model_div.find('.//a')
	if not 'promo' in self.model:
            a.set('href','/computer/%s' % self.model['_id'])
        else:
            a.set('href','/promotion/%s' % self.model['parent'])
	if 'name' in self.model and not self.this_is_cart:
	    a.text=self.model['name']
	else:
	    a.text = self.model['_id'][:-3]
	    strong= etree.Element('strong')
	    strong.text = self.model['_id'][-3:]
	    a.append(strong)
	price_span = self.model_div.find('.//span')
	price_span.set('id',self.model['_id'])
	self.components = buildPrices(self.model, self.json_prices, price_span)
	case_found = [c for c in self.components if c.cat_name == case]
	if len(case_found) >0:
	    if not 'promo' in self.model:
                self.icon.set('href','/computer/'+self.model['_id'])
            else:             
                self.icon.set('href','/promotion/'+self.model['parent'])
                pass
	    self.icon.find('img').set('src',case_found[0].getIconUrl())
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
	    h3.text = u'Пользовательская конфигурация'
	    if 'title' in self.model:
		h3.text = self.model['title']
		if 'name' in self.model:
		    h3.text = self.model['name'] + '. ' +h3.text
	    self.description_div.set('class','cart_description')
	self.container.append(self.description_div)


    def render(self):
	self.fillModelDiv()
	self.fillDescriptionDiv()
	if not self.this_is_cart:
	    self.model_div.set('id','m'+self.model['_id'])
	    if self.category in model_categories:
		if self.model['_id'] in model_categories[self.category]:
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

class NoteBookForCartPage(object):
    def __init__(self,notebook, note, key, icon, container):
	self.icon = icon
	self.notebook = notebook
	self.note = note
	self.container = container
	self.key = key

    def render(self):
	key = self.key
	note_name = self.note.xpath('//div[@class="cnname"]')[0]
	note_name.text = self.notebook['doc']['text']
	note_name.set('id',key+'_'+self.notebook['doc']['_id'])

	link = self.note.xpath('//strong[@class="modellink"]')[0]
	link.text = key[:-3]
	strong = etree.Element('strong')
	strong.text = key[-3:]
	link.append(strong)
	price = makeNotePrice(self.notebook['doc'])

	self.note.xpath('//span[@class="modelprice"]')[0].text = unicode(price) + u' р.'

	# icon = deepcopy(tree.find('model_icon').find('a'))
	self.icon.find('img').set('src',getComponentIcon(self.notebook['doc']))
	self.note.insert(0,self.icon)
	self.container.append(self.note)


def computers(template,skin,request):
    if globals()['gChoices'] is None:
	d = fillChoices()
	d.addCallback(lambda some: computers(template, skin, request))
	return d

    splitted = request.path.split('/')
    name = unicode(unquote_plus(splitted[-1]), 'utf-8')
    # cart is only /cart/12345. for /cart and for /computer - all models are shown
    this_is_cart = len(name) > 0 and name != 'computer' and name != 'cart'
    def render(result):

	models = [row['doc'] for row in result['rows'] if 'doc' in row and row['doc'] is not None]
	#fix cookies here!
	total = 0
	if not this_is_cart:
	    models = sorted(models,lambda x,y: x['order']-y['order'])
	else:
	    def sort(m1,m2):
		if u''.join(m1['date'])>u''.join(m2['date']):
		    return 1
		return -1
	    models = sorted(models,sort)
	    template.middle.remove(template.middle.find('div'))

	tree = template.root()
	container = template.middle.xpath('//div[@id="models"]')[0]

	json_prices = {}
	# TODO! make model view as for ComponentForModelsPage!!!!!!!!
	for m in models:

	    view = ModelForModelsPage(request, m, deepcopy(tree.find('model')),
				      this_is_cart,json_prices,
				      deepcopy(tree.find('model_icon').find('a')),
				      container)
	    view.render()
	    total +=1

	# TODO! make model view as for ComponentForModelsPage!!!!!!!!
	if 'notebooks' in result and 'user_doc' in result:
	    total_notes = []
	    need_cleanup = False
	    note_div = template.root().find('notebook').find('div')
	    clear_div = etree.Element('div')
	    clear_div.set('style','clear:both')
	    container.append(clear_div)
	    for n in result['notebooks']['rows']:
		if not 'doc' in n:
		    need_cleanup = True
		    continue
		if n['doc'] is None:
		    need_cleanup = True
		    continue
		keys = [(k,v) for k,v in result['user_doc']['notebooks'].items() if v == n['doc']['_id']]
		if len(keys) == 0:
		    need_cleanup = True
		    continue
		key = keys[0][0]
		note_view = NoteBookForCartPage(n,deepcopy(note_div),key,
						deepcopy(tree.find('model_icon').find('a')),
						container)
		note_view.render()
		total_notes.append(n['doc']['_id'])

	    # clean only for the owner of the cart!
	    if need_cleanup and request.getCookie('pc_key') == result['user_doc']['pc_key']:
		# some notes, possible will be deleted from store!
		to_clean = []
		for k,v in result['user_doc']['notebooks'].items():
		    if v not in total_notes:
			to_clean.append(k)
		for k in to_clean:

		    result['user_doc']['notebooks'].pop(k)
		# update user_doc
		couch.saveDoc(result['user_doc'])
		request.addCookie('pc_cart',
			  str(total+len(result['user_doc']['notebooks'])),
			  expires=datetime.now().\
				  replace(year=2038).strftime('%a, %d %b %Y %H:%M:%S UTC'),
			  path='/')

	_prices = 'undefined'

	if this_is_cart:
	    cart = deepcopy(template.root().find('top_cart'))
	    cart.xpath('//input[@id="cartlink"]')[0].set('value',"http://buildpc.ru/computer/"+name)
	    cart_divs = cart.findall('div')
	    for d in cart_divs:
		template.top.append(d)
	else:
	    _prices =simplejson.dumps(json_prices) + ';'
	    header = deepcopy(template.root().find('top_models'))
	    header_divs = header.findall('div')
	    for d in header_divs:
		template.top.append(d)

	template.middle.find('script').text = 'var prices=' + _prices;

	category = request.args.get('cat',[None])[0]

	if category is not None and category in model_categories_titles:
	    title = skin.root().xpath('//title')[0]
	    title.text = model_categories_titles[category]
	else:
	    title = skin.root().xpath('//title')[0]
	    title.text = u'Готовые модели компьютеров'

	skin.top = template.top
	skin.middle = template.middle
	return skin.render()

    # RENDER MODELS HERE!!!
    if not this_is_cart:
	d = couch.openView(designID,'models',include_docs=True,stale=False)
	d.addCallback(render)
    # RENDER cart here!!!!
    else:
	d = couch.openDoc(name)
	def glueModelsAndNotes(li, _user):
	    models = li[0][1]
	    notebooks = li[1][1]
	    # notebook_keys = li[1][1][0]
	    models['notebooks'] = notebooks
	    # models['notebook_keys'] = notebook_keys
	    models['user_doc'] = _user
	    return models
	def getModelsAndNotes(user_doc):
	    models = couch.listDoc(keys=user_doc['models'], include_docs=True)
	    if not 'notebooks' in user_doc:
		return models
	    notes = couch.listDoc(keys=[v for v in user_doc['notebooks'].values()], include_docs=True)
	    # notes.addCallback(lambda res: (user_doc['notebooks'],res))
	    d = defer.DeferredList((models, notes))
	    d.addCallback(glueModelsAndNotes, user_doc)
	    return d
	d.addCallback(getModelsAndNotes)
	d.addCallback(render)
    return d



def findComponent(model, name):
    """ ??? i have a flat choices now! why do i need that?"""
    code = model['items'][name]
    if type(code) is list:
	code = code[0]
    if code is None or code.startswith('no'):
	return noComponentFactory({},name)
    replaced = False
    retval = globals()['gChoices_flatten'][code] if code in globals()['gChoices_flatten'] else None
    if retval is None:
	retval = replaceComponent(code,model)
	replaced = True
    else:
	if retval['stock1'] == 0:
	    retval = replaceComponent(code,model)
	    replaced = True
    # there is 1 thing downwhere count! is is installed just in this component!
    ret = deepcopy(retval)
    ret['replaced'] = replaced
    return ret



def getComponentIcon(component, indexExtractor=lambda imgs: imgs[0]):
    retval = "/static/icon.png"
    if 'description' in component and'imgs' in component['description']:
	retval = ''.join(("/image/",component['_id'],"/",
			  indexExtractor(component['description']['imgs']),'.jpg'))
    return retval


class ComponentForModelsPage(object):
    def __init__(self,model,component, cat_name, price):
	self.component= component
	self.price = price
	self.cat_name = cat_name
	self.model = model

    def getIconUrl(self):
	return getComponentIcon(self.component)

    def render(self):
	li = etree.Element('li')
        li.text = self.component['text']
	if not 'promo' in self.model:
             li.text+= u' <strong>'+ unicode(self.price) + u' р</strong>'
	li.set('id',self.model['_id']+'_'+self.component['_id'])
	return li




# TODO! refactor it without side effects
# TODO! rename it. it is absoluttely about no prices!
def buildPrices(model, json_prices, price_span):
    aliasses_reverted = {}
    total = 0
    __components = []
    for k,v in parts_aliases.items():
	aliasses_reverted.update({v:k})
    def updatePrice(_id, catalogs, required_catalogs, price):
	if catalogs == required_catalogs:
	    if _id in json_prices:
		json_prices[_id].update({aliasses_reverted[required_catalogs]:price})
	    else:
		json_prices[_id] = {aliasses_reverted[required_catalogs]:price}

    for cat_name,code in model['items'].items():
	count = 1
	if type(code) is list:
	    count = len(code)
	    code = code[0]
	component_doc = findComponent(model,cat_name)
	code = component_doc['_id']
	price = makePrice(component_doc)*count
	total += price
	updatePrice(model['_id'],cat_name,displ,price)
	updatePrice(model['_id'],cat_name,soft,price)
	updatePrice(model['_id'],cat_name,audio,price)
	updatePrice(model['_id'],cat_name,mouse,price)
	updatePrice(model['_id'],cat_name,kbrd,price)
	__components.append(ComponentForModelsPage(model,component_doc, cat_name, price))
    if model['installing']:
	total += INSTALLING_PRICE
    if model['building']:
	 total += BUILD_PRICE
    if model['dvd']:
	total += DVD_PRICE
    price_span.text = str(total) + u' р'
    json_prices[model['_id']]['total'] = total
    return sorted(__components, lambda c1,c2:parts[c1.cat_name]-parts[c2.cat_name])


def lastUpdateTime():
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

def index(template, skin, request):

    if globals()['gChoices'] is None:
	d = fillChoices()
	d.addCallback(lambda some: index(template, skin, request))
	return d

    def buildProcAndVideo(components):
        proc_video = {}
        for c in components:
            if c.cat_name == proc:
                proc_video['proc_code'] = c.component['_id']
                proc_video['proc_catalog'] = getCatalogsKey(c.component)
                if 'brand' in c.component:
                    proc_video['brand'] = c.component['brand']
                if 'cores' in c.component:
                    proc_video['cores'] = c.component['cores']
                if 'cache' in c.component:
                    proc_video['cache'] = c.component['cache']
            elif c.cat_name == video:
                proc_video['video_code'] = c.component['_id']
                proc_video['video_catalog'] = getCatalogsKey(c.component)
        return proc_video

    def render(result):
	i = 0
	models = sorted([row['doc'] for row in result['rows']],lambda x,y: x['order']-y['order'])
	tree = template.root()
	div = template.middle.xpath('//div[@id="computers_container"]')[0]
	json_prices = {}
        json_procs_and_videos = {}
	# TODO! make model view as for ComponentForModelsPage!!!!!!!!
	for m in models:
	    model_snippet = tree.find('model')
	    snippet = deepcopy(model_snippet.find('div'))
	    snippet.set('style',"background-image:url('" + imgs[i] + "')")
	    a = snippet.find('.//a')
	    a.set('href','/computer/%s' % m['_id'])
	    a.text=m['name']
	    price_span = snippet.find('.//span')
	    price_span.set('id',m['_id'])
	    components = buildPrices(m, json_prices, price_span)
            json_procs_and_videos.update({m['_id']:buildProcAndVideo(components)})
	    div.append(snippet)
	    i+=1
	    if i==len(imgs): i=0
	template.middle.find('script').text = 'var prices=' + simplejson.dumps(json_prices) + ';'+\
            'var procs_videos=' + simplejson.dumps(json_procs_and_videos) + ';'
	last_update = template.middle.xpath('//span[@id="last_update"]')[0]
	last_update.text = lastUpdateTime()

	skin.top = template.top
	skin.middle = template.middle
	return skin.render()

    d = couch.openView(designID,'models',include_docs=True,stale=False)
    d.addCallback(render)
    return d


def updateOriginalModelPrices():
    def update(models):
	for row in models['rows']:
	    model = row['doc']
	    model['original_prices'] = {}
	    for name,code in model['items'].items():
		if type(code) is list:
		    code = code[0]
		if code in globals()['gChoices_flatten']:
		    component = globals()['gChoices_flatten'][code]
		    model['original_prices'].update({code:component['price']})
		else:
		    model['original_prices'].update({code:99})
	    couch.saveDoc(model)
    d = couch.openView(designID,'models',include_docs=True,stale=False)
    d.addCallback(update)



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


def makeNotePrice(doc):
    our_price = doc['price']*Course+NOTE_MARGIN
    return int(round(our_price/10))*10


def notebooks(template, skin, request):
    if globals()['gChoices'] is None:
	d = fillChoices()
	d.addCallback(lambda some: notebooks(template, skin, request))
	return d

    def render(result):
	json_notebooks= {}
	for r in result['rows']:

	    r['doc']['price'] = makeNotePrice(r['doc'])

	    note_div = deepcopy(template.root().find('notebook').find('div'))
	    note_div.set('class',r['doc']['_id']+' note')


	    link = note_div.xpath("//div[@class='nname']")[0].find('a')
	    name = getNoteBookName(r['doc'])
	    link.text = name
	    if 'ourdescription' in r['doc']:
		link.set('href','/notebook/'+name)
	    else:
		link.set('name',name)

	    for d in template.middle.xpath("//div[@class='notebook_column']"):
		clone = deepcopy(note_div)
		sort_div = clone.xpath("//div[@class='nprice']")[0]
		if d.get('id') == "s_price":
		    sort_div.text = unicode(r['doc']['price'])+u' р.'
		if d.get('id') == "s_size":
		    sort_div.text = getNoteDispl(r['doc'])
		if d.get('id') == "s_size":
		    sort_div.text = getNoteDispl(r['doc'])
		if d.get('id') == "s_performance":
		    sort_div.text = getNotePerformance(r['doc'])
		d.append(clone)

	    for token in ['id', 'flags','inCart',
			  'ordered','reserved','stock1', '_rev', 'warranty_type']:
		r['doc'].pop(token)
	    r['doc']['catalogs'] = getCatalogsKey(r['doc'])
	    #TODO save all this shit found from re
	    json_notebooks.update({r['doc']['_id']:r['doc']})

	template.middle.find('script').text = 'var notebooks=' + simplejson.dumps(json_notebooks)
	title = skin.root().xpath('//title')[0]
	title.text = u'Ноутбуки Asus'
	skin.top = template.top
	skin.middle = template.middle
	return skin.render()
    asus_12 = ["7362","7404","7586"]
    asus_14 = ["7362","7404","7495"]
    asus_15 = ["7362","7404","7468"]
    asus_17 = ["7362","7404","7704"]
    d = couch.openView(designID,'catalogs',include_docs=True,stale=False,
		       keys = [asus_12,asus_14,asus_15,asus_17])
    d.addCallback(render)
    return d

class ZipConponents(Resource):

    def getPriceAndCode(self, row):
	return {row['doc']['_id']:makePrice(row['doc'])}

    def render_GET(self, request):
	mothers = []
	procs = []
	videos = []
	for sockets in globals()['gChoices'][mother]:
	    mothers.append(sockets[1][1]['rows'])
	for sockets in globals()['gChoices'][proc]:
	    procs.append(sockets[1][1]['rows'])
	for sockets in globals()['gChoices'][video]:
	    for r in sockets[1][1]['rows']:
		videos.append(self.getPriceAndCode(r))

	mothers_mapping = {}
	for m in mothers:
	    if len(m)==0:continue
	    cats = getCatalogsKey(m[0]['doc'])
	    mothers_mapping.update({tuple(cats):m})
	proc_mapping = {}
	for p in procs:
	    if len(p)==0:continue
	    cats = getCatalogsKey(p[0]['doc'])
	    proc_mapping.update({tuple(cats):p})
	mother_procs = []
	for tu in mother_to_proc_mapping:
	    tm = tuple(tu[0])
	    tp = tuple(tu[1])
	    if  tm in mothers_mapping and tp in proc_mapping:
		mother_procs.append([[self.getPriceAndCode(c) for c in mothers_mapping[tm]],
				     [self.getPriceAndCode(c) for c in proc_mapping[tp]]])

	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	return simplejson.dumps({'mp':mother_procs,'v':videos})


class CatalogsFor(Resource):
    def render_GET(self, request):
	codes = request.args.get('c',[])
	if len(codes)==0:
	    request.finish()
	res = {}
	for c in codes:
	    res.update({c:getCatalogsKey(globals()['gChoices_flatten'][c])})
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	return simplejson.dumps(res)


class NamesFor(Resource):
    def render_GET(self, request):
	codes = request.args.get('c',[])
	if len(codes)==0:
	    request.finish()
	res = {}
	for c in codes:
	    component = globals()['gChoices_flatten'][c]
	    res.update({c:component['text'] + ' <strong>'+unicode(makePrice(component)) + u' р</strong>'})
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	return simplejson.dumps(res)

class ParamsFor(Resource):
    def render_GET(self, request):
	_type = request.args.get('type',[None])[0]
	if _type is None:
	    return "ok"
	codes = request.args.get('c',[])
	if len(codes)==0:
	    request.finish()
	res = {}
	for c in codes:
	    component = globals()['gChoices_flatten'][c]
	    if _type == 'proc':
		res.update({c:
			    {'brand':component['brand'] if 'brand' in component else '',
			    'cores':component['cores'] if 'cores' in component else '',
			    'cache':component['cache'] if 'cache' in component else ''}
			    })
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	return simplejson.dumps(res)

def renderPromotion(doc, template, skin):
    template.top.find('h1').text = doc['name']
    stuff = template.middle.xpath('//table[@id="promostuff"]')[0]
    record = template.root().find('record')

    def setImage(img, src):
	img.set('src','/image/'+doc['_id']+'/'+src)
    components = {}
    for c in sorted(doc['components'],lambda x,y:x['order']-y['order']):
	rec = deepcopy(record)
	tr = rec.find('tr')
	tds = tr.findall('td')
	tds[0].find('img').set('src','/static/promotion/'+c['type']+'.png');
	tds[-1].text = c['name']
	tr.set('id', c['code'])
	stuff.append(tr)
	if c['order'] == 10:
	    i = template.middle.xpath('//div[@id="promo_image"]')[0].find('img')
	    setImage(i,c['top_image'])
	    desc = template.middle.xpath('//div[@id="promo_description"]')[0]
	    p = etree.Element('p')
	    p.text = c['description']
	    desc.append(p)
	    if 'bottom_images' in c:
		for i in c['bottom_images']:
		    img = etree.Element('img')
		    setImage(img,i)
		    p.append(img)
	components.update({c['code']:c})

    scr = template.middle.find('script')
    scr.text = 'var _id="'+doc['_id']+'";var components='+simplejson.dumps(components)+';'
    scr.text += 'var parts = ' + simplejson.dumps(parts_aliases) + ';'
    template.top.xpath('//div[@id="promo_title"]')[0].text = doc['title']
    template.top.xpath('//div[@id="promo_extra"]')[0].text = doc['extra']
    descr = template.top.xpath('//p[@id="promo_desc"]')[0]
    for el in html.fragments_fromstring(doc['description']):
        descr.append(el)
    template.top.xpath('//div[@id="pprice"]')[0].text = unicode(doc['our_price'])

    skin.top = template.top
    skin.middle = template.middle
    skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 300px;')
    skin.root().xpath('//div[@id="middle"]')[0].set('class','midlle_computer')
    return skin.render()

def promotion(template, skin, request):
    if globals()['gChoices'] is None:
	d = fillChoices()
	d.addCallback(lambda some: promotion(template, skin, request))
	return d

    splitted = request.path.split('/')
    name = unicode(unquote_plus(splitted[-1]), 'utf-8')
    if len(name) == 0 or name=='promotion':
	name = 'ajax'
    d = couch.openDoc(name)
    d.addCallback(renderPromotion, template, skin)
    return d
