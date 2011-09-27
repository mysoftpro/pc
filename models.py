# -*- coding: utf-8 -*-
from pc.couch import couch, designID
from lxml import etree
from twisted.internet import defer
from string import Template
from urllib import quote_plus, unquote_plus
import simplejson
import re
from copy import deepcopy
import cgi

# <catalog id="7388" name="Материнские платы">
#       <catalog id="17961" name="LGA1155">
#       <catalog id="12854" name="LGA1156">
#       <catalog id="18029" name="LGA1366 Dual Core (процессоры Intel Nehalem )">
#       <catalog id="7449" name="LGA775 Dual Core (процессоры Intel)">
#       <catalog id="7627" name="SOCKET 478">
#       <catalog id="7699" name="SOCKET AM2 3 (процессоры AMD)">
#      <catalog id="2899" name="Материнские платы с процессором">

# <catalog id="7399" name="Процессоры">
#        <catalog id="18027" name="LGA1155">
#        <catalog id="18028" name="LGA1156">
#        <catalog id="9422" name="LGA1366">
#        <catalog id="7451" name="LGA775 Dual&amp;Quad Core">
#        <catalog id="7700" name="SOCKET AM2">

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

audio = "7365"
audio_20 = [audio,"7389", "7447"]
audio_21 = [audio,"7389", "7448"]
audio_51 = [audio,"7389", "7462"]

soft = "7369"
microsoft = "14570"
windows = [soft,microsoft,"14571"]

mother_to_proc_mapping= [(mother_1155,proc_1155),
                         (mother_1156,proc_1156),
                         (mother_1366,proc_1366),
                         (mother_775,proc_775),
                         (mother_am23,proc_am23),
                         (mother_fm1,proc_fm1)]


def getCatalogsKey(doc):
    if type(doc['catalogs'][0]) is dict:
        cats = []
        for c in doc['catalogs']:
            cats.append(str(c['id']))
        return cats
    return doc['catalogs']


# TODO! models must be stored in db and cached HERE
# to make opportunity to change the model without restart
# change in db and than clear cache


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



Margin=1.2
Course = 29.5

def makePrice(doc):
    if doc['price'] == 0:
        return 0
    course = Course
    if getCatalogsKey(doc) == windows:
        course = 1
    our_price = doc['price']*Margin*course
    # doc['price'] = int(str(round(our_price)).split('.')[0])
    return int(str(round(our_price)).split('.')[0])


def cleanDoc(doc, price):
    new_doc = {}
    for token in doc:
        if token in ['id', 'text', '_attachments','description','flags','inCart',
                     'ordered','reserved','stock1', '_rev', 'warranty_type']:
            continue
        if token == 'catalogs':
            new_doc.update({token:getCatalogsKey(doc)})
        else:
            new_doc.update({token:doc[token]})
    new_doc['price'] = price
    return new_doc

imgs = ['static/acer-aspire-ie-3450-desktop-pc-1.png',
        'static/compaq-presario-sg3440il-desktop-pc1.png',
        'static/dell-studio-hybrid-desktop-pc1.png',
        'static/desktop-pc1.png'
        ]



parts = {mother:0, proc:10, video:20, hdd:30, ram:40,
         case:50, sound:70, network:80, displ:90,
         audio:100, soft:110,
         kbrd:120, mouse:130, audio:140}

parts_names = {proc:u'Процессор', ram:u'Память',
               video:u'Видеокарта', hdd:u'Жесткий диск', case:u'Корпус',
               sound:u'Звуковая карта',
               network:u'Сетевая карта',
               mother:u'Материнская плата',displ:u'Монитор',
               audio:u'Аудиосистема', kbrd:u'Клавиатура', mouse:u'Мышь',
               soft:u'ОС'}




def replaceComponent(code,model):
    name = nameForCode(code,model)
    choices = globals()['gChoices'][name]
    def sameCatalog(doc):
        retval = True
        if mother==name:
            retval = model['mother_catalogs'] == getCatalogsKey(doc)
        if proc==name:
            retval = model['proc_catalogs'] == getCatalogsKey(doc)
        return retval

    flatten = []

    if type(choices) is list:
        for el in choices:
            if el[0]:
                for ch in el[1][1]['rows']:
                    flatten.append(ch['doc'])
    else:
        for ch in choices['rows']:
            flatten.append(ch['doc'])

    # TODO! sort em by price. not by code
    keys = [doc['_id'] for doc in flatten]
    keys.append(code)
    keys = sorted(keys)
    _length = len(keys)
    ind = keys.index(code)
    _next = ind+1
    if _next == _length:
        _next = ind-1
    next_el = deepcopy(flatten[_next])
    return next_el


no_component_added = False

def renderComputer(model, template, skin):
    _name = ''
    _uuid = '';
    h2 =template.top.find('div').find('h2')
    if 'name' in model:
        _name= model['name']
    elif '_id' in model:
        _name = model['_id']
        _uuid = model.pop('_id')
        for token in ('author','parent'):
            if token in model:
                model.pop(token)
    h2.text = _name
    original_viewlet = template.root().find('componentviewlet')

    choices = globals()['gChoices']

    model_json = {}
    tottal = 0
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

    def noComponentFactory(_doc):
        no_name = 'no' + name
        no_doc = deepcopy(_doc)
        no_doc['_id'] = no_name
        no_doc['price'] = 0
        no_doc['text'] = u'нет'
        return no_doc


    def noComponent(name, component_doc, rows):
        #hack!
        component_doc['catalogs'] = getCatalogsKey(rows[0]['doc'])

        if globals()['no_component_added']:return
        if name not in [mouse,kbrd,displ,soft,audio, network]: return
        no_doc = noComponentFactory(component_doc)
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


    def fillViewlet(_doc):
        tr = viewlet.find("tr")
        tr.set('id',name)
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

        # if name in our_descriptions:
        #     our.text = our_descriptions[name]
        clear = etree.Element('div')
        clear.set('style','clear:both;')
        clear.text = ''


        d_comments = ''
        d_name = ''
        if 'description' in _doc:
            d_name = _doc['description']['name']
            d_comments = _doc['description']['comments']
            if 'imgs' in _doc['description']:
                for i in _doc['description']['imgs']:
                    img = etree.Element('img')
                    img.set('src', '/image/' + _doc['_id'] + '/' + i + '.jpg')
                    img.set('align','right')
                    manu.text += etree.tostring(img)

        manu.text += d_name + d_comments

        descr.append(manu);
        descr.append(our)
        descr.append(clear)
        return descr


    for name,code in model['items'].items():
        component_doc = None
        count = 0
        if code is None:
            component_doc = noComponentFactory({})
        else:

            if type(code) is list:
                count = len(code)
                code = code[0]
                counted.update({code:count})

            component_doc = findComponent(model,name)

        if count >0:
            component_doc.update({'count':count})

        viewlet = deepcopy(original_viewlet)
        descr = fillViewlet(component_doc)


        price = makePrice(component_doc)

        tottal += price

        cleaned_doc = cleanDoc(component_doc, price)
        cleaned_doc['price'] = price
        model_json.update({cleaned_doc['_id']:cleaned_doc})
        viewlet.xpath('//td[@class="component_price"]')[0].text = unicode(price) + u' р'

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

    template.middle.find('script').text = u''.join(('var model=',simplejson.dumps(model_json),
                                                    ';var uuid=',simplejson.dumps(_uuid),
                                                    ';var tottal=',unicode(tottal),
                                                    ';var choices=',simplejson.dumps(components_json),
                                                    ';var parts_names=',simplejson.dumps(parts_names),
                                                    ';var mother_to_proc_mapping=',
                                                    simplejson.dumps(mother_to_proc_mapping),
                                                    ';var proc_to_mother_mapping=',
                                                    simplejson.dumps([(el[1],el[0]) for el in mother_to_proc_mapping]),
                                                    ';var Course=',str(Course),
                                                    ';var parts=',simplejson.dumps({
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
                    })
                                                    ))

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
                                                   .addCallback(lambda res:('LGA7755',res)),
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
                                                  'catalogs',include_docs=True, key=case_exclusive, stale=False)
                                    .addCallback(lambda res: (u"Эксклюзивные корпусы",res))])
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
        return globals()['gChoices'] #new_res
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
    return d

def computers(template,skin,request):
    if globals()['gChoices'] is None:
        d = fillChoices()
        d.addCallback(lambda some: computers(template, skin, request))
        return d

    splitted = request.path.split('/')
    name = unicode(unquote_plus(splitted[-1]), 'utf-8')

    def render(result):
        models = [row['doc'] for row in result['rows']]
        if len(name) == 0:
            models = sorted(models,lambda x,y: x['order']-y['order'])
        else:
            def sort(m1,m2):
                if u''.join(m1['date'])>u''.join(m2['date']):
                    return 1
                return -1
            models = sorted(models,sort)
        tree = template.root()
        container = template.middle.xpath('//div[@id="models"]')[0]
        for m in models:
            model_snippet = tree.find('model')
            divs = deepcopy(model_snippet.findall('div'))
            model_div = divs[0]
            # snippet.set('style',"background-image:url('" + m[imgs[i] + "')")
            if '_attachments' in m and 'icon.png' in m['_attachments']:
                model_div.set('style',"background-image:url('/image/" + m['_id'] + "/icon.png')")
            a = model_div.find('.//a')
            a.set('href','/computer/%s' % m['_id'])
            if 'name' in m:
                a.text=m['name']
            else:
                a.text = m['_id']
            price_span = model_div.find('.//span')
            price_span.set('id',m['_id'])
            tottal = 0
            componets = []
            for cat_name,code in m['items'].items():
                component_doc = findComponent(m,cat_name)
                tottal += makePrice(component_doc)
                componets.append(component_doc)
            price_span.text = str(tottal) + u' р'
            container.append(model_div)

            description_div = divs[1]
            h3 = description_div.find('h3')
            if 'title' in m:
                h3.text = m['title']
            else:
                h3.text = u'Пользовательская конфигурация'
            if 'description' in m:
                description_div.append(etree.fromstring(m['description']))
            else:
                ul = etree.Element('ul')
                for c in componets:
                    li = etree.Element('li')
                    li.text = c['text']
                    ul.append(li)
                description_div.append(ul)
                description_div.set('style','width:750px !important')                
            container.append(description_div)

        if len(name)>0:
            cart = deepcopy(template.root().find('top_cart'))
            cart.xpath('//input[@id="cartlink"]')[0].set('value',"http://buildpc.ru/computer/"+name)
            cart_divs = cart.findall('div')
            for d in cart_divs:
                template.top.append(d)
        else:
            header = deepcopy(template.root().find('top_models'))
            header_divs = header.findall('div')
            for d in header_divs:
                template.top.append(d)

        skin.top = template.top
        skin.middle = template.middle
        return skin.render()

    if len(name) == 0:
        d = couch.openView(designID,'models',include_docs=True,stale=False)
        d.addCallback(render)
    else:
        # TODO! listDoc. do not use view here!!!!!!!!!!!!!!
        d = couch.openView(designID,'user_models',include_docs=True,stale=False, key=name)
        d.addCallback(render)

    return d









def findComponent(model, name):
    code = model['items'][name]
    if type(code) is list:
        code = code[0]
    choices = globals()['gChoices'][name]
    retval = None
    if type(choices) is list:
        for el in choices:
            if el[0]:
                for ch in el[1][1]['rows']:
                    if ch['doc']['_id'] == code:
                        retval = ch['doc']
                        break
    else:
        for ch in choices['rows']:
            if ch['doc']['_id'] == code:
                retval = ch['doc']
                break
    if retval is None:
        retval = replaceComponent(code,model)
    else:
        if retval['stock1'] == 0:
            retval = replaceComponent(code,model)
    return retval



def index(template, skin, request):

    if globals()['gChoices'] is None:
        d = fillChoices()
        d.addCallback(lambda some: index(template, skin, request))
        return d

    def render(result):
        i = 0

        models = sorted([row['doc'] for row in result['rows']],lambda x,y: x['order']-y['order'])
        tree = template.root()
        div = template.middle.xpath('//div[@id="computers_container"]')[0]
        for m in models:
            model_snippet = tree.find('model')
            snippet = deepcopy(model_snippet.find('div'))
            snippet.set('style',"background-image:url('" + imgs[i] + "')")
            a = snippet.find('.//a')
            a.set('href','/computer/%s' % m['_id'])
            a.text=m['name']
            price_span = snippet.find('.//span')
            price_span.set('id',m['_id'])
            tottal = 0
            for cat_name,code in m['items'].items():
                component_doc = findComponent(m,cat_name)
                tottal += makePrice(component_doc)
            price_span.text = str(tottal) + u' р'
            div.append(snippet)
            i+=1
            if i==len(imgs): i=0
        skin.top = template.top
        skin.middle = template.middle
        return skin.render()

    d = couch.openView(designID,'models',include_docs=True,stale=False)
    d.addCallback(render)
    return d
