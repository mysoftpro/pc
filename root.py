# -*- coding: utf-8 -*-
from twisted.web.xmlrpc import Proxy

from twisted.python import log
import sys
from cStringIO import StringIO
from StringIO import StringIO as SIO
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
from pc.models import models, index, computer
from pc.catalog import XmlGetter
from urllib import quote_plus, unquote_plus
from twisted.web import proxy
from twisted.web.error import NoResource
from twisted.python.failure import Failure
from lxml import etree

_cached_statics = {}
global_cache = {}
static_dir = os.path.join(os.path.dirname(__file__), 'static')



static_hooks = {
    'index.html':index,
    'computer.html':computer
}



class Template(object):

    def __init__(self, f=None):
	# skin
	if f is None:
	    f = open(os.path.join(static_dir, 'skin.html'))
	parser = etree.HTMLParser(encoding='utf-8')
	self.tree = etree.parse(f, parser)
	f.close()

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



class CachedStatic(File):

    def __init__(self, *args, **kwargs):
	File.__init__(self, *args, **kwargs)
	self.skin = Template()
	# f = open(os.path.join(static_dir, 'skin.html'))
	# self.skin = Template(f.read())
	# f.close()

    def render(self, request):
	return self.render_GET(request)



    def render_GET(self, request):
	# request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	# print "---------------cached---------------------"
	# print _cached_statics.keys()

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
	virtual_name = unquote_plus(request.path.split('/')[-1])

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

	if request.setLastModified(last_modified) is CACHED and physical_name_in_cache:#(physical_name_in_cache or virtual_name_in_cache):
	    return ''

	if physical_name_in_cache:
	    return _cached_statics[physical_name][1]

	# if virtual_name_in_cache:
	#     return _cached_statics[virtual_name][1]

	else:
	    if '.html' in fileForReading.name or '.json' in fileForReading.name:
		name_to_cache = physical_name
		# DO NOT CACHE VIRTUAL NAMES. UNCOMMENT ALL TO CACHE EM
		if len(virtual_name)>0:
		    splitted = physical_name.split('\\')
		    if len(splitted) == 0:
			splitted = physical_name.split('/')
		    if splitted[-1] != virtual_name:
			name_to_cache = None # virtual_name
		d = self.renderTemplate(fileForReading, last_modified, request)
		d.addCallback(self._gzip, name_to_cache, last_modified)
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
	short_name = None
	if '/' in fileForReading.name:
	    short_name = fileForReading.name.split('/')[-1]
	else:
	    short_name = fileForReading.name.split('\\')[-1]

	if short_name in static_hooks:
	    # parser = etree.HTMLParser(encoding='utf-8')
	    # tree = etree.parse(fileForReading, parser)
	    template = Template(f=fileForReading)
	    d = static_hooks[short_name](template, self.skin, request)
	else:
	    # just an empty snippet
	    d = defer.Deferred()
	    content = fileForReading.read()
	    d.addCallback(lambda x: content)
	fileForReading.close()
	return d


    def render_GSIPPED(self, gzipped, request):
	request.write(gzipped)
	request.finish()

class Root(Resource):
    def __init__(self, host_url, index_page):
	Resource.__init__(self)
	self.static = CachedStatic(static_dir)
	self.static.indexNames = [index_page]
	self.putChild('static',self.static)
	self.putChild('xml',XmlGetter())
	self.putChild('computer', Desktop())
	self.putChild('carts', Carts())
	self.putChild('component', Component())
	self.putChild('image', ImageProxy())
	self.putChild('save', Save())
	self.host_url = host_url
	self.cookies = []
	reactor.callLater(0, self.collectCookies)

    def collectCookies(self):
	d = couch.get('/_uuids?count=20')
	def append(uuids):
	    for uuid in simplejson.loads(uuids)['uuids']:
		self.cookies.append(uuid)
	d.addCallback(append)

    def getChild(self, name, request):
	user_cookie = request.getCookie('pc_user')
	if  user_cookie is None:
	    cookie = self.cookies.pop()
	    request.addCookie('pc_user',
			      str(cookie), expires=datetime.now().replace(year=2038).strftime('%a, %d %b %Y %H:%M:%S UTC'))
	    if len(self.cookies) < 10:
		reactor.callLater(0, self.collectCookies)
	u = str(request.URLPath())
	if ('http://' + self.host_url + '/' == u) or 'favicon' in name:
	    return self.static.getChild(name, request)
	return self





class Desktop(Resource):
    def __init__(self, *args, **kwargs):
	self.static = CachedStatic(static_dir)
	Resource.__init__(self, *args, **kwargs)
    def getChild(self, name, request):
	return self.static.getChild("computer.html", request)

# TODO!!!! / at the end of the name!!!
class Carts(Resource):
    def __init__(self, *args, **kwargs):
	self.static = CachedStatic(static_dir)
	Resource.__init__(self, *args, **kwargs)
    def getChild(self, name, request):
	splitted = request.path.split('/')
	print splitted
	if splitted[-1] == '':
	    splitted = splitted[:-1]
	if splitted[-1] != name:
	    return self
	return self.static.getChild("computer.html", request)



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

    def finish(self, user_doc, request, model_id):
	print 'will finish'
	request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
	doc = {'id':model_id}
	request.write(simplejson.dumps(doc))
	request.finish()

    def saveModel(self, user_doc, user_id, model, request):

	if user_doc.__class__ is Failure:
	    user_doc = {'_id':user_id, 'models':{}, 'date':str(date.today()).split('-')}

	if not 'id' in model:
	    d = couch.get('/_uuids?count=1')
	    def addId(uuids):
		model['id'] = simplejson.loads(uuids)['uuids'][0]
		return user_doc
	    d.addCallback(addId)
	    d.addCallback(self.saveModel, user_id, model, request)
	    return d
	else:
	    model_id = model.pop('id')
	    user_doc['models'].update({model_id:model})
	    print user_doc
	    d = couch.saveDoc(user_doc)
	    d.addCallback(self.finish, request, model_id)
	    return d

    def pr(self, e):
	print e

    # def storeUser(self, error, user_id, model, request):
    #     print "storeeeeeeeeeeeeeeeeeee!!"
    #     user_doc = {'models':{}, 'date':str(date.today()).split('-')}
    #     d = couch.saveDoc(user_doc, user_id)
    #     d.addCallback(self.saveModel, model, request)
    #     d.addErrback(self.pr)

    def render_GET(self, request):
	model = request.args.get('model', [None])[0]
	if model is not None:
	    jmodel = simplejson.loads(model)
	    user_id = request.getCookie('pc_user')
	    d = couch.openDoc(user_id)
	    d.addCallback(self.saveModel, user_id, jmodel, request)
	    d.addErrback(self.saveModel, user_id, jmodel, request)
	    # d.addErrback(self.storeUser, user_id, jmodel, request)
	    return NOT_DONE_YET
	return 'fail'

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
