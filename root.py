# -*- coding: utf-8 -*-

from cStringIO import StringIO
import gzip
from twisted.web.resource import Resource, ForbiddenResource
from twisted.web.static import File, getTypeAndEncoding
from twisted.internet import reactor, defer
from pc.jsmin import jsmin
from pc import base36
from twisted.web.server import NOT_DONE_YET
import os
from twisted.web.http import CACHED
from pc.couch import couch, designID
import simplejson
from datetime import datetime, date
from pc.models import index, computer, computers,parts,\
    noComponentFactory,makePrice,parts_names,parts,updateOriginalModelPrices,\
    BUILD_PRICE,INSTALLING_PRICE,DVD_PRICE
from pc.catalog import XmlGetter
from twisted.web import proxy
from twisted.web.error import NoResource
from twisted.python.failure import Failure
from lxml import etree, html
from copy import deepcopy
from pc.mail import Sender


def simplePage(template, skin, request):
    skin.top = template.top
    skin.middle = template.middle
    skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 190px;')
    skin.root().xpath('//div[@id="middle"]')[0].set('class','midlle_how')
    d = defer.Deferred()
    d.addCallback(lambda some:skin.render())
    d.callback(None)
    return d

parts_aliases = {
    'motherboard':('how_7388', u'Как выбирать материнскую плату'),
    'processor':('how_7396', u'Как выбирать процессор'),
    'video':('how_7406', u'Как выбирать видеокарту'),
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
    # try:
    els = html.fragments_fromstring(doc['html'])
    container.text = ''
    for el in els:
        if type(el) is unicode:
            container.text +=el
        else:
            container.append(el)
    template.top.find('h1').text = header
    skin.top = template.top
    skin.middle = template.middle
    skin.root().xpath('//div[@id="gradient_background"]')[0].set('style','min-height: 230px;')
    skin.root().xpath('//div[@id="middle"]')[0].set('style','margin-top: -90px;')
    return skin

def partPage(template, skin, request):
    name = request.path.split('/')[-1]
    d = couch.openDoc(parts_aliases[name][0])
    d.addCallback(renderPartPage, parts_aliases[name][1], template, skin)
    d.addCallback(lambda some:some.render())
    return d


static_hooks = {
    'index.html':index,
    'computer.html':computer,
    'computers.html':computers,
    'howtochoose.html':simplePage,
    'howtouse.html':simplePage,
    'howtobuy.html':simplePage,
    'warranty.html':simplePage,
    'part.html':partPage
    }



_cached_statics = {}

static_dir = os.path.join(os.path.dirname(__file__), 'static')


class SiteMap(Resource):
    def buildElement(self, location, freq="monthly", prior="0.8"):
	url = etree.Element('url')
	loc = etree.Element('loc')
	loc.text = 'http://buildpc.ru/'+location
	lastmod = etree.Element('lastmod')
	today = datetime.today()
	lastmod.text = '-'.join((str(today.year),str(today.month),str(today.day)))
	changefreq = etree.Element('changefreq')
	changefreq.text = freq
	priority = etree.Element('priority')
	priority.text = prior
	url.append(loc)
	url.append(lastmod)
	url.append(changefreq)
	url.append(priority)
	return url

    def siteMap(self, models, request):
	request.setHeader('Content-Type', 'text/xml;charset=utf-8')
	root = etree.XML('<urlset></urlset>')
	root.append(self.buildElement(''))
	root.append(self.buildElement('computer'))
	for model in models['rows']:
	    root.append(self.buildElement('computer/'+model['key'], freq='daily'))
	root.append(self.buildElement('howtochoose'))
	root.append(self.buildElement('howtobuy'))
	root.append(self.buildElement('howtouse'))
	root.append(self.buildElement('warranty'))
	request.write(etree.tostring(root, encoding='utf-8', xml_declaration=True))
	request.finish()

    def render_GET(self, request):
	d = couch.openView(designID, 'models')
	d.addCallback(self.siteMap, request)
	return NOT_DONE_YET


class Template(object):

    def __init__(self, opened_file, name_to_cache, last_modified):
	cache = globals()['_cached_statics']
	if name_to_cache in cache and cache[name_to_cache][0] == last_modified:
	    self.tree = deepcopy(cache[name_to_cache][1])
	else:
	    parser = etree.HTMLParser(encoding='utf-8')
	    cache[name_to_cache] = (last_modified,etree.parse(opened_file, parser))
	    self.tree = deepcopy(cache[name_to_cache][1])
	opened_file.close()

    def root(self):
	return self.tree.getroot().find('body')

    def render(self):
	return etree.tostring(self.tree, encoding='utf-8', method="html")


    def get_middle(self):
	return self.root().find('.//middle')

    def set_middle(self, middle):
	parent = self.get_middle().getparent()
	# REFACTOR
	div = etree.Element('div')
	div.set('id','middle')
	for el in middle:
	    div.append(el)
	parent.replace(self.get_middle(), div)
	# parent.replace(self.get_middle(), middle)

    middle = property(get_middle, set_middle)


    def get_top(self):
	return self.root().find('.//top')

    def set_top(self, top):
	parent = self.get_top().getparent()
	# REFACTOR
	div = etree.Element('div')
	div.set('id','top')
	for el in top:
	    div.append(el)
	parent.replace(self.get_top(), div)

    top = property(get_top, set_top)



class Skin(Template):
    def __init__(self):
	cache = globals()['_cached_statics']
	name_to_cache = 'skin.html'
	if name_to_cache in cache:
	    self.tree = deepcopy(cache[name_to_cache])
	else:
	    opened_file = open(os.path.join(static_dir, name_to_cache))
	    parser = etree.HTMLParser(encoding='utf-8')
	    cache[name_to_cache] = etree.parse(opened_file, parser)
	    self.tree = deepcopy(cache[name_to_cache])
	    opened_file.close()


class CachedStatic(File):

    def __init__(self, *args, **kwargs):
	self.skin = Skin()
	File.__init__(self, *args, **kwargs)

    def render(self, request):
	return self.render_GET(request)



    def render_GET(self, request):
	self.restat(False)

	if self.type is None:
	    self.type, self.encoding = getTypeAndEncoding(self.basename(),
							  self.contentTypes,
							  self.contentEncodings,
							  self.defaultType)

	if 'image' in self.type:
	    if hasattr(File, 'render_GET'):
		return File.render_GET(self, request)
	    else:
		return File.render(self, request)

	if not self.exists():
	    return self.childNotFound.render(request)

	if self.isdir():
	    return self.redirect(request)

	request.setHeader('accept-ranges', 'bytes')


	try:
	    fileForReading = self.openForReading()
	except IOError, e:
	    import errno
	    if e[0] == errno.EACCES:
		return ForbiddenResource().render(request)
	    else:
		raise

	physical_name = fileForReading.name
	# virtual_name = unquote_plus(request.path.split('/')[-1])

	if 'jpg' in physical_name or 'gif' in physical_name or 'png' in physical_name or physical_name == 'jScrollPane.js':
	    request.setHeader("Cache-Control", "max-age=290304000, public")
	else:
	    request.setHeader("Cache-Control", "max-age=0, must-revalidate")#7200

	request.setHeader('Content-Encoding', 'gzip')

	if 'html' in self.type or 'text' in self.type:
	    self.type += ';charset=utf-8'
	request.setHeader('Content-Type', self.type)
	last_modified = self.getmtime()
	# 304 is here
	physical_name_in_cache = physical_name in _cached_statics and _cached_statics[physical_name][0] == last_modified
	# virtual_name_in_cache = virtual_name in _cached_statics and _cached_statics[virtual_name][0] == last_modified

	if physical_name_in_cache and request.setLastModified(last_modified) is CACHED:
	    return ''

	if physical_name_in_cache:
	    return _cached_statics[physical_name][1]
	# if virtual_name_in_cache:
	#     return _cached_statics[virtual_name][1]

	else:
	    if '.html' in fileForReading.name or '.json' in fileForReading.name:
		# name_to_cache = physical_name
		# DO NOT CACHE VIRTUAL NAMES. UNCOMMENT ALL TO CACHE EM
		# if len(virtual_name)>0:
		#     splitted = physical_name.split('\\')
		#     if len(splitted) == 0:
		#         splitted = physical_name.split('/')
		#     if splitted[-1] != virtual_name:
		#         name_to_cache = None # virtual_name
		d = self.renderTemplate(fileForReading, last_modified, request)
		d.addCallback(self._gzip, None, last_modified)
		d.addCallback(self.render_GSIPPED, request)
		return NOT_DONE_YET
	    else:
		content = fileForReading.read()
		fileForReading.close()
		return self._gzip(content, physical_name, last_modified)



    def _gzip(self, _content,_name, _time):
	if _name is not None and "js" in _name and "min." not in _name:
	    _content = jsmin(_content)
	buff = StringIO()
	f = gzip.GzipFile(_name,'wb',9, buff)
	f.write(_content)
	f.close()
	buff.seek(0)
	gzipped = buff.read()
	buff.close()
	if _name is not None:
	    _cached_statics[_name] = (_time, gzipped)
	return gzipped


    def renderTemplate(self, fileForReading, last_modified, request):
	self.prepareSkin(request)
	short_name = None
	if '/' in fileForReading.name:
	    short_name = fileForReading.name.split('/')[-1]
	else:
	    short_name = fileForReading.name.split('\\')[-1]

	if short_name in static_hooks:
	    template = Template(fileForReading,short_name,last_modified)
	    d = static_hooks[short_name](template, self.skin, request)
	else:
	    # just an empty snippet
	    d = defer.Deferred()
	    content = fileForReading.read()
	    d.addCallback(lambda x: content)
	fileForReading.close()
	return d


    def prepareSkin(self, request):
	pass

    def render_GSIPPED(self, gzipped, request):
	request.write(gzipped)
	request.finish()

class Cookable(Resource):
    def __init__(self):
	self.cookies = []
	Resource.__init__(self)

    def checkCookie(self, request):
	user_cookie = request.getCookie('pc_user')
	if  user_cookie is None:
	    request.addCookie('pc_user',
			      base36.gen_id(),
			      expires=datetime.now().replace(year=2038).strftime('%a, %d %b %Y %H:%M:%S UTC'),
			      path='/')


class Root(Cookable):
    def __init__(self, host_url, index_page):
	Cookable.__init__(self)
	self.static = CachedStatic(static_dir)
	self.static.indexNames = [index_page]


	self.putChild('static',self.static)
	self.putChild('computer', TemplateRenderrer(self.static, 'computers.html','computer.html'))
	self.putChild('cart', TemplateRenderrer(self.static, 'computers.html','computers.html'))
	self.putChild('howtochoose', TemplateRenderrer(self.static, 'howtochoose.html'))
	self.putChild('howtouse', TemplateRenderrer(self.static, 'howtouse.html'))
	self.putChild('howtobuy', TemplateRenderrer(self.static, 'howtobuy.html'))
	self.putChild('warranty', TemplateRenderrer(self.static, 'warranty.html'))

	self.putChild('motherboard', TemplateRenderrer(self.static, 'part.html'))
	self.putChild('processor', TemplateRenderrer(self.static, 'part.html'))
	self.putChild('video', TemplateRenderrer(self.static, 'part.html'))
	self.putChild('ram', TemplateRenderrer(self.static, 'part.html'))
	self.putChild('hdd', TemplateRenderrer(self.static, 'part.html'))
	self.putChild('ram', TemplateRenderrer(self.static, 'part.html'))
	self.putChild('case', TemplateRenderrer(self.static, 'part.html'))
	self.putChild('display', TemplateRenderrer(self.static, 'part.html'))
	self.putChild('keyboard', TemplateRenderrer(self.static, 'part.html'))
	self.putChild('mouse', TemplateRenderrer(self.static, 'part.html'))
	self.putChild('audio', TemplateRenderrer(self.static, 'part.html'))

	self.putChild('xml',XmlGetter())
	self.putChild('component', Component())
	self.putChild('image', ImageProxy())
	self.putChild('save', Save())
	self.putChild('delete',Delete())
	self.putChild('sender', Sender())
	self.putChild('select_helps', SelectHelpsProxy())
	self.putChild('admin',Admin())
	self.host_url = host_url
	self.putChild('5406ae5f1ec4.html',File(os.path.join(static_dir,'5406ae5f1ec4.html')))
	self.putChild('sitemap.xml',SiteMap())
	self.putChild('robots.txt',File(os.path.join(static_dir,'robots.txt')))

    def getChild(self, name, request):
	self.checkCookie(request)
	u = str(request.URLPath())
	if ('http://' + self.host_url + '/' == u) or 'favicon' in name:
	    return self.static.getChild(name, request)
	return self



class TemplateRenderrer(Cookable):
    def __init__(self, static, name, default_name=None):
	Cookable.__init__(self)
	self.static = static
	self.name = name
	self.default_name = default_name

    def render_GET(self, request):
	self.checkCookie(request)
	return self.static.getChild(self.name, request).render_GET(request)

    def getChild(self, name, request):
	self.checkCookie(request)
	child = None
	if self.default_name is None:
	    child = Cookable.getChild(self.name,request)
	else:
	    child = self.static.getChild(self.default_name, request)
	return child



class CustomWriter(object):
    def __init__(self, viewName):
	self.strio = StringIO()
	self.gzipfile = gzip.GzipFile(viewName, 'wb', 9, self.strio)

    def write(self, data):
	self.gzipfile.write(data)
    def read(self):
	self.gzipfile.close()
	return self.strio.getvalue()

    def close(self):
	self.strio.close()


class Component(Resource):
    isLeaf = True
    allowedMethods = ('GET',)
    def writeComponent(self, doc, request):
	if 'description' in doc:
	    request.write(simplejson.dumps(doc['description']))
	else:
	    request.write(simplejson.dumps({'name':'','comments':'','img':[],'imgs':[]}))
	request.finish()

    def render_GET(self, request):
	_id = request.args.get('id', [None])[0]
	if _id is None: return simplejson.dumps({'name':'','comments':'','img':[],'imgs':[]})
	if 'no' in _id: return simplejson.dumps({'name':'','comments':'','img':[],'imgs':[]})
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	d = couch.openDoc(_id)
	d.addCallback(self.writeComponent, request)
	return NOT_DONE_YET



class Save(Resource):

    def finish(self, user_model, request, user_doc):
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	if user_model[0][0] and user_model[1][0]:
	    request.addCookie('pc_cart',
			      str(len(user_doc['models'])),
			      expires=datetime.now().replace(year=2038).strftime('%a, %d %b %Y %H:%M:%S UTC'),
			      path='/')
	    request.write(simplejson.dumps(user_model[1][1]))
	else:
	    request.write(simplejson.dumps({}))
	request.finish()

    def render_GET(self, request):
	model = request.args.get('model', [None])[0]
	if model is not None:
	    jmodel = simplejson.loads(model)
	    # TODO validate fields to avoid hacks!
	    user_id = request.getCookie('pc_user')
	    d1 = couch.openDoc(user_id)
	    d2 = defer.Deferred()
	    model_id = None
	    if 'id' in jmodel:
		model_id = jmodel.pop('id')
		d2 = couch.openDoc(model_id)
	    else:
		model_id = base36.gen_id()
		d2.addCallback(lambda x: jmodel)
		d2.callback(None)
	    li = defer.DeferredList([d1,d2])
	    li.addCallback(self.saveModel, user_id, model_id, jmodel, request)
	    return NOT_DONE_YET
	return 'fail'

    # TODO! how fast is base36.gen_id() ???? may be wrap in deferred???
    def saveModel(self, user_model, user_id, model_id, new_model, request):
	from pc import models
	user_doc = None
	if user_model[0][0]:
	    user_doc = user_model[0][1]
	else:
	    user_doc = {'_id':user_id, 'models':[]}

	model_doc = None
	if user_model[1][0]:
	    edit_model = request.args.get('edit', [None])[0] is not None
	    if edit_model:
		same_author = user_model[1][1]['author'] == user_id
		not_processing = not 'processing' in user_model[1][1] \
		    or not user_model[1][1]['processing']
		if same_author and not_processing:
		    model_doc = user_model[1][1]
		else:
		    model_doc = new_model
		    model_doc['_id'] = model_id
	    else:
		model_doc = new_model
		model_doc['_id'] = model_id
	else:
	    model_doc = new_model
	    model_doc['_id'] = model_id

	# no it does not matter what we have in model_doc.
	# brand new or existant model. just copy all fron new model here
	for k,v in new_model.items():
	    model_doc[k] = v
	model_doc['original_prices'] = {}
	for name,code in model_doc['items'].items():
	    if type(code) is list:
		code = code[0]
	    if code in models.gChoices_flatten:
		component = models.gChoices_flatten[code]
		model_doc['original_prices'].update({code:component['price']})
	    else:
		model_doc['original_prices'].update({code:0})

	model_doc['author'] = user_id
	if model_doc['_id'] not in user_doc['models']:
	    user_doc['models'].append(model_doc['_id'])
	_date=str(date.today()).split('-')
	user_doc['date'] = _date
	model_doc['date'] = _date
	d1 = couch.saveDoc(user_doc)
	d2 = couch.saveDoc(model_doc)
	li = defer.DeferredList([d1,d2])
	li.addCallback(self.finish, request,user_doc)


def get_uuid():
    d = defer.Deferred()
    d.addCallback(lambda some: base36.gen_id())
    d.callback(None)
    return d

class Delete(Resource):
    def render_GET(self, request):
	uuid = request.args.get('uuid', [None])[0]
	user_id = request.getCookie('pc_user')
	model = couch.openDoc(uuid)
	user = couch.openDoc(user_id)
	def delete(user_model):
	    if not user_model[0][0] or not user_model[1][0]:
		request.write('fail')
		request.finish()
		return
	    _user = user_model[0][1]
	    _model = user_model[1][1]
	    if _model['author'] == user_id and ('processing' not in _model or not _model['processing']):
		couch.deleteDoc(uuid,_model['_rev'])
		_user['models'] = [m for m in _user['models'] if m != _model['_id']]
		couch.saveDoc(_user)
		request.write('ok')
		request.finish()
	    request.write('fail')
	    request.finish()
	defer.DeferredList([user,model]).addCallback(delete)
	return NOT_DONE_YET



# http://localhost:5984/pc/18060/L0JlbnFfbGNkL1Y5MjAuanBn.jpg
class ImageProxy(Resource):
    def __init__(self, *args, **kwargs):
	Resource.__init__(self, *args, **kwargs)
	self.proxy = proxy.ReverseProxyResource('127.0.0.1', 5984, '/pc', reactor=reactor)

    def getChild(self, path, request):
	last = request.uri.split('/')[-1]

	# safety to not show couch internals
	# just check that it endswith image extension and no parameters in it
	if '?' in last or '&' in last:
	    return NoResource()
	image = last.endswith('.jpg')
	image = image or last.endswith('.jpeg')
	image = image or last.endswith('.png')
	image = image or last.endswith('.gif')

	if not image:
	    return NoResource()

	return self.proxy.getChild(path, request)


class SelectHelpsProxy(Resource):
    def __init__(self, *args, **kwargs):
	Resource.__init__(self, *args, **kwargs)
	self.proxy = proxy.ReverseProxyResource('127.0.0.1', 5984, '/pc', reactor=reactor)

    def getChild(self, path, request):
	last = request.uri.split('/')[-1]

	# safety to not show couch internals
	# just check that it endswith image extension and no parameters in it
	if '?' in last or '&' in last:
	    return NoResource()
	_help = 'how_' in last
	if not _help:
	    return NoResource()
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	return self.proxy.getChild(last, request)

def clear_cache():
    globals()['_cached_statics'] = {}
    _dir = globals()['static_dir']
    for f in os.listdir(_dir):
	try:
	    os.utime(os.path.join(_dir,f), None)
	except:
	    pass
    from pc import models
    models.no_component_added = False
    models.gChoices = None
    models.gChoices_flatten = {}
    models.gWarning_sent = []
    d = models.fillChoices()
    d.addCallback(lambda x: models.updateOriginalModelPrices())

class ClearCache(Resource):
    def render_GET(self, request):
	clear_cache()
	return "ok"

class UpdatePrices(Resource):
    # this thing is only update prices in models.
    # not in components.
    # does not used actually (it is automatic)
    def render_GET(self,request):
	updateOriginalModelPrices()
	return "ok"

class ClearAttachments(Resource):
    def clear(self, result):
	def _sorted(name1,name2):
	    return int(name1.split('-')[0])-int(name1.split('-')[0])

	for r in result['rows']:
	    doc = r['doc']
	    if '_attachments' not in doc:
		continue
	    if len(doc['_attachments'].keys()) <= 3:
		continue
	    sorted_attachments = sorted([name for name in doc['_attachments'].keys() if 'jpg' not in name], _sorted)
	    for a in sorted_attachments[:-3]:
		doc['_attachments'].pop(a)
	    couch.saveDoc(doc)
    def render_GET(self, request):
	d = couch.openView(designID,"codes", include_docs=True, stale=False)
	d.addCallback(self.clear)
	return "ok"


from twisted.web.guard import HTTPAuthSessionWrapper, DigestCredentialFactory
from twisted.cred.checkers import FilePasswordDB
from twisted.cred.portal import IRealm, Portal
from zope.interface import implements
from twisted.web.resource import IResource


realm_dir = os.path.join(os.path.dirname(__file__), 'realm')

class Realm(object):
    implements(IRealm)
    def requestAvatar(self, avatarId, mind, *interfaces):
	if IResource in interfaces:
	    return (IResource, AdminGate(File(realm_dir)), lambda: None)
	raise NotImplementedError()

portal = Portal(Realm(), [FilePasswordDB('/home/aganzha/pswrds')])
credentialFactory = DigestCredentialFactory("md5", "buildpc.ru")
auth_wrapper = HTTPAuthSessionWrapper(portal, [credentialFactory])

class Admin(Resource):
    def render_GET(self, request):
	return "<html><body><h1>No way!</h1></body></html>"
    def getChild(self, name, request):
	return auth_wrapper.getChildWithDefault(name, request)

class AdminGate(Resource):
    def __init__(self, static):
	Resource.__init__(self)
	self.static = static
	self.putChild('clear_cache',ClearCache())
	self.putChild('clear_attachments',ClearAttachments())
	self.putChild('update_prices',UpdatePrices())
	self.putChild('edit_model', EditModel())
	self.putChild('couch',proxy.ReverseProxyResource('127.0.0.1', 5984,
							 '/_utils', reactor=reactor))
	self.putChild('findorder', FindOrder())
	self.putChild('storeorder', StoreOrder())
	self.putChild('storemodel', StoreModel())
	self.putChild('mothers', Mothers())
	self.putChild('store_mother', StoreMother())
	self.putChild('videos', Videos())
	self.putChild('store_video', StoreVideo())
	self.putChild('warranty', WarrantyFill())
	self.putChild('show_how', ShowHow())
	self.putChild('edit_how', EditHow())

    def render_GET(self, request):
	return self.static.getChild('index.html', request).render(request)

    def getChild(self, name, request):
	if 'html' in name or 'js' in name or 'jpg' in name:
	    return self.static.getChild(name, request)
	return self


class Mothers(Resource):
    def finish(self, result, request):
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	request.write(simplejson.dumps(result))
	request.finish()

    def render_GET(self, request):
	from pc import models
	defer.DeferredList([
		couch.openView(designID,
			       'catalogs',
			       include_docs=True, key=models.mother_1155, stale=False),
		# .addCallback(lambda res: ("LGA1155",res)),
		couch.openView(designID,
			       'catalogs',
			       include_docs=True, key=models.mother_1156, stale=False),
		# .addCallback(lambda res: ("LGA1166",res)),
		couch.openView(designID,
			       'catalogs',
			       include_docs=True, key=models.mother_775, stale=False),
		# .addCallback(lambda res: ("LGA775",res)),
		couch.openView(designID,
			       'catalogs',
			       include_docs=True, key=models.mother_am23, stale=False),
		# .addCallback(lambda res: ("AM2 3",res)),
		couch.openView(designID,
			       'catalogs',
			       include_docs=True, key=models.mother_fm1, stale=False)
		# .addCallback(lambda res: ("FM1",res))
		]).addCallback(self.finish, request)
	return NOT_DONE_YET


class Videos(Resource):
    def finish(self, result, request):
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	request.write(simplejson.dumps(result))
	request.finish()

    def render_GET(self, request):
	from pc import models
	defer.DeferredList([
		couch.openView(designID,
			       'catalogs',
			       include_docs=True, key=models.geforce, stale=False),
		# .addCallback(lambda res: ("GeForce",res)),
		couch.openView(designID,
			       'catalogs',
			       include_docs=True, key=models.radeon, stale=False),
		# .addCallback(lambda res: ("Radeon",res)),
		]).addCallback(self.finish, request)
	return NOT_DONE_YET


class FindOrder(Resource):

    def graceFull(self, fail, request):
	self.finish((((False, fail),),), request)


    def finish(self, result, request):
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	# first level
	for li in result:
	    for tu in li:
		if not tu[0]:
		    request.write(simplejson.dumps({'fail':str(tu[1])}))
		    request.finish()
		    return
	request.write(simplejson.dumps(result))
	request.finish()


    def addComponents(self, model_user):
	defs = []

	def addCount(count):
	    def add(doc):
		doc['count'] = count
		return doc
	    return add

	def addText(text):
	    def _text(doc):
		doc['text'] = text
		return doc
	    return _text

	def addWarranty(warranty):
	    def _warranty(doc):
		doc['warranty_type'] = warranty
		return doc
	    return _warranty

	def popDesc():
	    def _pop(doc):
		if 'description' in doc:
		    doc.pop('description')
		if '_attachments' in doc:
		    doc.pop('_attachments')
		return doc
	    return _pop

	def addPrice(ourPrice=None):
	    def add(doc):
		if ourPrice is None:
		    doc['ourprice'] = makePrice(doc)
		else:
		    doc['ourprice'] = ourPrice
		return doc
	    return add

	def addName(name):
	    def add(doc):
		doc['humanname'] = name
		return doc
	    return add

	def addOrder(order):
	    def add(doc):
		doc['order'] = order
		return doc
	    return add

	def wrap(co):
	    d = defer.Deferred()
	    d.addCallback(lambda x: co)
	    d.callback(None)
	    return d

	def cheapestDVD(res):
	    cheapeast = None
	    for row in res['rows']:
		if cheapeast is None:
		    cheapeast = row['doc']
		else:
		    if row['doc']['price'] < cheapeast['price']:
			cheapeast = row['doc']
	    return cheapeast
	from pc import models
	from copy import deepcopy
	for k,v in model_user[0][1]['items'].items():
	    component = None
	    if v is not None:
		if type(v) is list:
		    # component = couch.openDoc(v[0])
		    # TODO! what if no component in choices?????????
		    component = wrap(deepcopy(models.gChoices_flatten[v[0]]))
		    component.addCallback(addCount(len(v)))
		else:
		    if not v.startswith('no'):
			# component = couch.openDoc(v)
			component = wrap(deepcopy(models.gChoices_flatten[v]))
			component.addCallback(addCount(1))
		    else:
			component = wrap(noComponentFactory({}, k))
	    else:
		component = wrap(noComponentFactory({}, k))
	    component.addCallback(addPrice())
	    component.addCallback(popDesc())
	    component.addCallback(addName(parts_names[k]))
	    component.addCallback(addOrder(parts[k]))
	    defs.append(component)

	if model_user[0][1]['dvd']:
	    dvds = couch.openView(designID,
				  'dvd',
				  stale=False, include_docs=True)
	    dvds.addCallback(cheapestDVD)
	    dvds.addCallback(addPrice(DVD_PRICE))
	    dvds.addCallback(popDesc())
	    dvds.addCallback(addName(u'DVD'))
	    dvds.addCallback(addCount(1))
	    dvds.addCallback(addOrder(300))
	    defs.append(dvds)

	def makeServiseRecord(_id, name, text, price, warranty, order):
	    service = defer.Deferred()
	    service.addCallback(lambda x: {'_id':_id})
	    service.addCallback(addName(name))
	    service.addCallback(addText(text))
	    service.addCallback(addPrice(price))
	    service.addCallback(addCount(1))
	    service.addCallback(addWarranty(warranty))
	    service.addCallback(addOrder(order))
	    service.callback(None)
	    defs.append(service)
	if model_user[0][1]['building']:
	    makeServiseRecord('building',u'Сборка',
			      u'Сборка компьютера',BUILD_PRICE,
			      u'6 месяцев',400)
	if model_user[0][1]['installing']:
			makeServiseRecord('installing',u'Установка',
			      u'Установка программного обеспечения',INSTALLING_PRICE,
			      u'без гарантии',500)

	li = defer.DeferredList(defs)
	li.addCallback(lambda res: (model_user,res))
	return li


    def getModel(self, error, _id, request):
	d = couch.openDoc(_id)
	d1 = couch.openDoc(request.getCookie('pc_user'))
	model_user = defer.DeferredList([d,d1])
	model_user.addCallback(self.addComponents)
	model_user.addCallback(self.finish, request)
	return model_user

    def render_GET(self, request):
	_id = request.args.get('id')[0]
	order_d = couch.openDoc('order_'+_id)
	order_d.addCallback(self.finish, request)
	# if no order -> get model
	order_d.addErrback(self.getModel, _id, request)
	# if problem with the order -> finish any way
	order_d.addErrback(self.graceFull, request)
	return NOT_DONE_YET

# REMEMBER! each order linked to model by id!
# somewhone make an order for several models will have some orders
class StoreOrder(Resource):
    def finish(self, order_res, model_rev, request):
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	request.write(str(order_res['rev'])+'.'+str(model_rev))
	request.finish()

    def storeOrder(self, model_res, order, model, request):
	model['_rev'] = model_res['rev']
	order['model'] = model
	d = couch.saveDoc(order)
	d.addCallback(self.finish, model['_rev'], request)

    def render_POST(self, request):
	order = request.args.get('order')[0]
	jorder = simplejson.loads(order)
	jorder['date']=str(date.today()).split('-')
	model = jorder['model']
	model['processing'] = True
	d = couch.saveDoc(model)
	d.addCallback(self.storeOrder, jorder,model,request)
	return NOT_DONE_YET

class StoreMother(Resource):
    def finish(self, doc, request):
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	request.write(str(doc['rev']))
	request.finish()

    def render_POST(self, request):
	mother = request.args.get('mother')[0]
	jmother = simplejson.loads(mother)
	d = couch.saveDoc(jmother)
	d.addCallback(self.finish, request)
	return NOT_DONE_YET



class StoreVideo(Resource):
    def finish(self, doc, request):
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	request.write(str(doc['rev']))
	request.finish()

    def render_POST(self, request):
	video = request.args.get('video')[0]
	jvideo = simplejson.loads(video)
	d = couch.saveDoc(jvideo)
	d.addCallback(self.finish, request)
	return NOT_DONE_YET


class StoreModel(Resource):
    def finish(self, some, request):
	request.write('ok')
	request.finish()

    def createHow(self, fail, _id, descr):
	how = {'_id':_id, 'html':descr}
	return couch.saveDoc(how)

    def storeHow(self, how, description):
	how['html'] = description
	return couch.saveDoc(how)

    def storeModel(self, model, to_store, request):
	for k,v in to_store['model'].items():
	    if k in model:
		model[k] = v
	d = couch.saveDoc(model)

	names = sorted(parts.keys(),lambda x,y: parts[x]-parts[y])
	defs = []
	for name,descr in zip(names,to_store['hows']):
	    _d= couch.openDoc('how_'+name)
	    _d.addCallback(self.storeHow,descr)
	    _d.addErrback(self.createHow,descr,'how_'+name)
	    defs.append(_d)
	hows_d = defer.DeferredList(defs)
	whole_d = defer.DeferredList((d,hows_d))
	whole_d.addCallback(self.finish, request)
	return whole_d

    def render_POST(self, request):
	to_store = request.args.get('to_store')[0]
	jto_store = simplejson.loads(to_store)
	d = couch.openDoc(jto_store['_id'])
	d.addCallback(self.storeModel, jto_store,request)
	return NOT_DONE_YET



class EditModel(Resource):
    def getChild(self, name, request):
	static = CachedStatic(static_dir)
	child = static.getChild("computer.html", request)
	script = etree.Element('script')
	script.set('type','text/javascript')
	# script.set('src','../edit_model.js')
	script.text ='head.ready(function(){head.js("../edit_model.js");});'
	child.skin.root().append(script)
	return child

#TODO! what if the user will change the model when order already processed!
# it need to prohibit that
class WarrantyFill(Resource):
    def fail(self, fail, request):
	request.write('fail')
	request.finish()
    def finish(self, doc, request):
	res = []
	model = doc['model']
	for c in doc['components']:
	    code = c['_id']
	    if code.startswith('no'):
		continue
	    record = {'name':c['text'],
		      'price':c['ourprice'],
		      'pcs':c['count']}
	    record.update({'factory':doc['factory_idses'][code]})
	    record.update({'warranty':c['warranty_type']})
	    res.append(record)
	ob = {'items':res}
	ob.update({'building':model['building']})
	ob.update({'installing':model['building']})
	ob.update({'dvd':model['dvd']})

	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	request.write(simplejson.dumps(ob))
	request.finish()

    def render_GET(self, request):
	_id = request.args.get("_id", [None])[0]
	if _id is None:
	    return "fail"
	d = couch.openDoc('order_'+_id)
	d.addCallback(self.finish, request)
	# d.addErrback(self.fail, request)
	return NOT_DONE_YET


class ShowHow(Resource):
    def finish(self, res, request):
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	request.write(simplejson.dumps(res))
	request.finish()

# ('how_7388','how_7396','how_7406','how_7394','how_7383',
#                      'how_7369','how_7387','how_7390','how_7389')
    def render_POST(self,request):
	defs = []
	for name in parts_aliases.values():
	    defs.append(couch.openDoc(name[0]))
	li = defer.DeferredList(defs)
	li.addCallback(self.finish, request)
	return NOT_DONE_YET

class EditHow(Resource):

    def finish(self, res, request):
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	request.write(simplejson.dumps(res))
	request.finish()

    def render_POST(self,request):
	doc = request.args.get('doc',[None])[0]
	d = couch.saveDoc(simplejson.loads(doc))
	d.addCallback(self.finish, request)
	return NOT_DONE_YET
