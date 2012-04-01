# -*- coding: utf-8 -*-
from twisted.internet import defer
from lxml import etree, html
from pc.couch import couch, designID

simple_titles = {
    '/howtochoose':u' Как выбирать компьютер',
    '/howtouse':u'Как пользоваться сайтом',
    '/howtobuy':u'Как покупать',
    '/warranty':u'Гарантии',
    '/support':u'Поддержка',
    '/about':u'Про магазин',
    '/whyauth':u'Зачем нужна авторизация',
    '/upgrade_set':u'Наборы для апгрейда',
}

def simplePage(template, skin, request):
    if request.path in simple_titles:
        title = skin.root().xpath('//title')[0]
        title.text = simple_titles[request.path]

    # skin.top = template.top
    # skin.middle = template.middle
    # skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 190px;')
    # skin.root().xpath('//div[@id="middle"]')[0].set('class','midlle_how')
    for el in template.top:
        skin.top.append(el)
    for el in template.middle:
        skin.middle.append(el)
    d = defer.Deferred()
    d.addCallback(lambda some:skin.render())
    d.callback(None)
    return d

parts_aliases = {
    'motherboard':('how_7388', u'Как выбирать материнскую плату'),
    'processor':('how_7399', u'Как выбирать процессор'),
    'video':('how_7396', u'Как выбирать видеокарту'),
    'hdd':('how_7394', u'Как выбирать жесткий диск'),
    'ram':('how_7369', u'Как выбирать память'),
    'case':('how_7387', u'Как выбирать корпус'),
    'display':('how_7390', u'Как выбирать монитор'),
    'keyboard':('how_7389', u'Как выбирать клавиатуру'),
    'mouse':('how_7383', u'Как выбирать мышь'),
    'audio':('how_7406', u'Как выбирать аудиосистему'),
}

def renderPartPage(doc, header, template, skin):

    container = template.middle.find('div')

    els = html.fragments_fromstring(doc['html'])
    container.text = ''
    for el in els:
        if type(el) is unicode:
            container.text +=el
        else:
            container.append(el)
    template.top.find('h1').text = header
    if doc['_id'] == 'how_7396':
        video_link = etree.Element('a')
        video_link.set('href','/videocard')
        video_link.text=u'Лучшие видеокарты для апгрейда'
        video_link.tail = u' собраны на '

        video_link1 = etree.Element('a')
        video_link1.set('href','/videocard')
        video_link1.text=u'отдельной странице.'

        d = etree.Element('div')
        d.append(video_link)
        d.append(video_link1)

        template.top.find('h1').getparent().insert(1,d)

    title = skin.root().xpath('//title')[0]
    title.text = header
    for el in template.top:
        skin.top.append(el)
    for el in template.middle:
        skin.middle.append(el)
    
    return skin

def partPage(template, skin, request):
    name = request.path.split('/')[-1]
    d = couch.openDoc(parts_aliases[name][0])
    d.addCallback(renderPartPage, parts_aliases[name][1], template, skin)
    d.addCallback(lambda some:some.render())
    return d

