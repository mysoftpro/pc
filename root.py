# -*- coding: utf-8 -*-
from twisted.web.xmlrpc import Proxy

from twisted.python import log
import sys
from cStringIO import StringIO
import gzip
from twisted.web.resource import Resource, ForbiddenResource
from twisted.web.static import File, getTypeAndEncoding
from twisted.internet import reactor, threads, defer
from pc.jsmin import jsmin
from twisted.web.server import NOT_DONE_YET
import os
from twisted.web.http import CACHED
from pc.couch import couch
import simplejson
from datetime import datetime, date
from pc.models import index, computer, computers
from pc.catalog import XmlGetter
from urllib import quote_plus, unquote_plus
from twisted.web import proxy
from twisted.web.error import NoResource
from twisted.python.failure import Failure
from lxml import etree
from copy import deepcopy
from pc.mail import Sender
_cached_statics = {}

static_dir = os.path.join(os.path.dirname(__file__), 'static')



static_hooks = {
    'index.html':index,
    'computer.html':computer,
    'computers.html':computers
}



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
	# parent.replace(self.get_top(), top)

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

	if 'html' in self.type:
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
	# not_min = "js" in _name and "min." not in _name
	# if not_min:
	#     _content = jsmin(_content)
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

	# Hoooooooooks
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
	reactor.callLater(0, self.collectCookies)
	Resource.__init__(self)
    def collectCookies(self):
	d = couch.get('/_uuids?count=20')
	def append(uuids):
	    for uuid in simplejson.loads(uuids)['uuids']:
		self.cookies.append(uuid[26:])
	d.addCallback(append)
    def getChild(self, name, request):
	user_cookie = request.getCookie('pc_user')
	if  user_cookie is None:
	    cookie = self.cookies.pop()
	    request.addCookie('pc_user',
			      str(cookie),
			      expires=datetime.now().replace(year=2038).strftime('%a, %d %b %Y %H:%M:%S UTC'),
			      path='/')
	    if len(self.cookies) < 10:
		reactor.callLater(0, self.collectCookies)

class Root(Cookable):
    def __init__(self, host_url, index_page):
	Cookable.__init__(self)
	self.static = CachedStatic(static_dir)
	self.static.indexNames = [index_page]
	self.putChild('static',self.static)
	self.putChild('xml',XmlGetter())
	self.putChild('clear_cache',ClearCache())
	self.putChild('computer', Computer(self.static))
	self.putChild('cart', Cart(self.static))
	self.putChild('component', Component())
	self.putChild('image', ImageProxy())
	self.putChild('save', Save())
	self.putChild('delete',Delete())
	self.putChild('sender', Sender())
	self.putChild('select_helps', SelectHelpsProxy())
	self.putChild('admin',Admin())
	self.host_url = host_url

    def collectCookies(self):
	d = couch.get('/_uuids?count=20')
	def append(uuids):
	    for uuid in simplejson.loads(uuids)['uuids']:
		self.cookies.append(uuid[26:])
	d.addCallback(append)

    def getChild(self, name, request):
	Cookable.getChild(self, name, request)
	u = str(request.URLPath())
	if ('http://' + self.host_url + '/' == u) or 'favicon' in name:
	    return self.static.getChild(name, request)
	return self

class Computer(Cookable):
    def __init__(self, static):
	Cookable.__init__(self)
	self.static = static
    
    def render_GET(self, request):
        return self.static.getChild("computers.html", request).render_GET(request)

    def getChild(self, name, request):
	Cookable.getChild(self, name, request)
	return self.static.getChild("computer.html", request)




class Cart(Cookable):
    def __init__(self, static):
	Cookable.__init__(self)
	self.static = static
    def getChild(self, name, request):
	Cookable.getChild(self, name, request)
	return self.static.getChild("computers.html", request)


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

    def finish(self, user_model, request):
	model_doc = user_model[1]
	user_doc = user_model[0]
	if model_doc['_id'] not in user_doc['models']:
	    user_doc['models'].append(model_doc['_id'])
	    request.addCookie('pc_cart',
			      str(len(user_doc['models'])),
			      expires=datetime.now().replace(year=2038).strftime('%a, %d %b %Y %H:%M:%S UTC'),
			      path='/')
	_date=str(date.today()).split('-')
	user_doc['date'] = _date
	model_doc['date'] = _date
	couch.saveDoc(model_doc)
	couch.saveDoc(user_doc)
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	doc = {'id':model_doc['_id']}
	request.write(simplejson.dumps(doc))
	request.finish()

    def saveModel(self, user_doc, user_id, model, request):
	def addId(uuids, _user, _model):
	    _model['_id'] = simplejson.loads(uuids)['uuids'][0][26:]
	    _model['author'] = _user['_id']
	    return (_user,_model)
	def updateModel(_model, _user, new_model):
	    # if _model author is _user: AND "EDIT" in request, just updateModel
	    # else - store new model with the parent_id of this model
	    if _model['author'] == _user['_id'] and request.args.get('edit', [None])[0] is not None:
		new_model['_id'] = _model['_id']
		new_model['_rev'] = _model['_rev']
		new_model['author'] = _user['_id']
		return (_user,_model)
	    else:
		new_model['parent'] = _model['_id']
		_d = couch.get('/_uuids?count=1')
		_d.addCallback(addId, _user, new_model)
		return _d
	# cases
	# 1 no user doc, no model
	if user_doc.__class__ is Failure:
	    if 'id' in model:
		model['parent'] = model.pop('id')
	    user_doc = {'_id':user_id, 'models':[], 'date':str(date.today()).split('-')}
	    d = couch.get('/_uuids?count=1')
	    d.addCallback(addId, user_doc, model)
	    d.addCallback(self.finish, request)
	    return d
	# 2a user doc but no model
	if not 'id' in model:
	    d = couch.get('/_uuids?count=1')
	    d.addCallback(addId, user_doc, model)
	    d.addCallback(self.finish, request)
	    return d
	# 2b user doc and model
	else:
	    model_id = model.pop('id')
	    d = couch.openDoc(model_id)
	    d.addCallback(updateModel,user_doc, model)
	    d.addCallback(self.finish, request)
	    return d

    def pr(self, e):
	print e

    def render_GET(self, request):
	model = request.args.get('model', [None])[0]
	if model is not None:
	    jmodel = simplejson.loads(model)
	    # TODO validate fields to avoid hacks!
	    user_id = request.getCookie('pc_user')
	    d = couch.openDoc(user_id)
	    d.addCallback(self.saveModel, user_id, jmodel, request)
	    d.addErrback(self.saveModel, user_id, jmodel, request)
	    # d.addErrback(self.storeUser, user_id, jmodel, request)
	    return NOT_DONE_YET
	return 'fail'


class Delete(Resource):
    def render_GET(self, request):
	uuid = request.args.get('uuid', [None])[0]
	user_id = request.getCookie('pc_user')
	model = couch.openDoc(uuid)
	user = couch.openDoc(user_id)
	## TODO! delete model from user_doc['models']
	## (open user_doc and assign callback to deferred list)
	def delete(user_model):
	    if not user_model[0][0] or not user_model[1][0]:
		request.write('fail')
		request.finish()
		return
	    _user = user_model[0][1]
	    _model = user_model[1][1]
	    #TODO cart key!!!!
	    if _model['author'] == user_id:
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
	_help = 'sh-' in last
	if not _help:
	    return NoResource()
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	return self.proxy.getChild(last, request)

class ClearCache(Resource):
    def render_GET(self, request):
	globals()['_cached_statics'] = {}
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
	self.putChild('bui',Bui())
	self.putChild('zui',Zui())
	# self.root = AdminRoot()
    def render_GET(self, request):
	return "Welcome admin"

    def getChild(self, name, request):
	if 'html' in name or 'js' in name:
	    return self.static.getChild(name, request)
	return self

class Bui(Resource):
    def render_GET(self, request):
	return "this is bui"


class Zui(Resource):
    def render_GET(self, request):
	return "zui zui zui zui"
