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
from pc.models import models, index
from pc.catalog import XmlGetter
from string import Template
from os import stat

_cached_statics = {}
global_cache = {}
static_dir = os.path.join(os.path.dirname(__file__), 'static')



static_hooks = {
    'index.html':index
}




slots_names = ['container', 'content']


class NamedSio(SIO):
    def __init__(self, name):
        self.name = name
        SIO.__init__(self)

class CachedStatic(File):

    def __init__(self, *args, **kwargs):
        File.__init__(self, *args, **kwargs)
        f = open(os.path.join(static_dir, 'skin.html'))
        self.skin = Template(f.read())
        f.close()



    def slot_path(self, slot_name):
        return self.path.replace(".html", "_"+slot_name+".html")


    def restat(self, reraise=True):
        """
        Re-calculate cached effects of 'stat'.  To refresh information on this path
        after you know the filesystem may have changed, call this method.

        @param reraise: a boolean.  If true, re-raise exceptions from
        L{os.stat}; otherwise, mark this path as not existing, and remove any
        cached stat information.
        """
        # tretiy3
        # calculate statinfo for last modified slot
        if 'html' in self.path:
            try:
                mtime = 0
                for s in slots_names:
                    stat_info = stat(self.slot_path(s))
                    if stat_info.st_mtime>mtime:
                        print "max!:"
                        print s
                        mtime = stat_info.st_mtime
                        self.statinfo = stat_info
                print "eeeeeeeeeeeeeeeeeeeeeeeeee"
                print self.statinfo
            except OSError:
                self.statinfo = 0
                if reraise:
                    raise
        else:
            try:
                self.statinfo = stat(self.path)
            except OSError:
                self.statinfo = 0
                if reraise:
                    raise

    def openForReading(self):
        """Open a file and return it."""
        # tretiy3
        if 'html' in self.path:
            sio = NamedSio(self.path)
            slots = {}
            for s in slots_names:
                f = open(self.slot_path(s))
                slots.update({s:f.read()})
                f.close()
            sio.write(self.skin.substitute(slots))
            sio.seek(0)
            return sio
        return self.open()

    def render(self, request):
        return self.render_GET(request)


    def render_GET(self, request):

        """
        tretiy3--------------------- this is just a copy of original render_GET with small changes

        Begin sending the contents of this L{File} (or a subset of the
        contents, based on the 'range' header) to the given request.
        """
        # request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
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

        # cache all images and min.js files
        fn = fileForReading.name

        print "----------------------"
        print fn

        if 'jpg' in fn or 'gif' in fn or 'png' in fn or fn == 'jScrollPane.js':
            request.setHeader("Cache-Control", "max-age=290304000, public")
        else:
            request.setHeader("Cache-Control", "max-age=0, must-revalidate")#7200

        # ct = zope.contenttype.guess_content_type(fileForReading.name, fileForReading)[0]
        request.setHeader('Content-Encoding', 'gzip')

        if 'html' in self.type:
            self.type += ';charset=utf-8'
        request.setHeader('Content-Type', self.type)
        last_modified = self.getmtime()

        print "[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[["
        print last_modified

        # do i need 304?
        if request.setLastModified(last_modified) is CACHED and fileForReading.name in _cached_statics and _cached_statics[fileForReading.name][0] == last_modified:
            print "30444444444444444444444444444444444"
            return ''

        if fileForReading.name in _cached_statics and _cached_statics[fileForReading.name][0] == last_modified:
            print "FROM CACHE"
            return _cached_statics[fileForReading.name][1]
        else:
            # d = threads.deferToThread(self.makeGzip, fileForReading, last_modified)
            d = self.makeGzip(fileForReading, last_modified)
            d.addCallback(self.render_GSIPPED, request)
            return NOT_DONE_YET

    def makeGzip(self, fileForReading, last_modified):
        if fileForReading.__class__ is NamedSio:
            content = fileForReading.getvalue()
        else:
            content = fileForReading.read()
        fileForReading.close()

        def _gzip(_content,_name, _time):
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

        # Hoooooooooks
        short_name = None
        if '/' in fileForReading.name:
            short_name = fileForReading.name.split('/')[-1]
        else:
            short_name = fileForReading.name.split('\\')[-1]
        d = defer.Deferred()
        if short_name in static_hooks:
            d = static_hooks[short_name](content)
            d.addCallback(_gzip, fileForReading.name, last_modified)
        else:
            d.addCallback(lambda x: content)
            d.addCallback(_gzip, fileForReading.name, last_modified)
            d.callback(None)
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
        self.putChild('model',Model())
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




class Model(Resource):
    def render_GET(self, request):
        model = request.args.get('name', [None])[0]
        if model is None:
            return 'null'
        model = unicode(model, 'utf-8')
        model_obs = [m for m in models if m['name'] == model]
        if len(model) >0:
            print model_obs
        return "ok"


class Computer(Resource):
    def __init__(self, *args, **kwargs):
        self.static = CachedStatic(static_dir)
        Resource.__init__(self, *args, **kwargs)
    def getChild(self, name, request):
        return self.static.getChild(name, request)
