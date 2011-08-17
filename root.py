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
from kalog.jsmin import jsmin
from twisted.web.server import NOT_DONE_YET
import os
from twisted.web.http import CACHED
from pc.couch import couch
import simplejson
from datetime import datetime, date
from pc.models import models, index, computer
from pc.catalog import XmlGetter
from urllib import quote_plus, unquote_plus

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
        virtual_name_in_cache = virtual_name in _cached_statics and _cached_statics[virtual_name][0] == last_modified

        if request.setLastModified(last_modified) is CACHED and (physical_name_in_cache or virtual_name_in_cache):
            return ''

        # cached gzip is here
        if physical_name_in_cache in _cached_statics:
            return _cached_statics[physical_name][1]

        if virtual_name_in_cache in _cached_statics:
            return _cached_statics[virtual_name][1]

        else:
            if '.html' in fileForReading.name or '.json' in fileForReading.name:
                name_to_cache = physical_name
                if len(virtual_name)>0:
                    splitted = physical_name.split('\\')
                    if len(splitted) == 0:
                        splitted = physical_name.split('/')
                    if splitted[-1] != virtual_name:
                        name_to_cache = virtual_name                        

                d = self.renderTemplate(fileForReading, last_modified, request)
                d.addCallback(self._gzip, name_to_cache, last_modified)
                d.addCallback(self.render_GSIPPED, request)
                return NOT_DONE_YET
            else:
                content = fileForReading.read()
                fileForReading.close()
                return self._gzip(content, physical_name, last_modified)



    def _gzip(self, _content,_name, _time):
        not_min = "js" in _name and "min." not in _name
        if not_min:
            _content = jsmin(_content)
        buff = StringIO()
        f = gzip.GzipFile(_name,'wb',9, buff)
        f.write(_content)
        f.close()
        buff.seek(0)
        gzipped = buff.read()
        buff.close()
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
        self.putChild('computer', Computer())
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
        if ('http://' + self.host_url + '/' == u):
            return self.static.getChild(name, request)
        return self





class Computer(Resource):
    def __init__(self, *args, **kwargs):
        self.static = CachedStatic(static_dir)
        Resource.__init__(self, *args, **kwargs)
    def getChild(self, name, request):
        return self.static.getChild("computer.html", request)
