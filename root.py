# -*- coding: utf-8 -*-
from twisted.web.xmlrpc import Proxy
import base64
from twisted.python import log
import sys
from cStringIO import StringIO
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

_cached_statics = {}
global_cache = {}
static_dir = os.path.join(os.path.dirname(__file__), 'static')

class CachedStatic(File):

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
        if 'jpg' in fn or 'gig' in fn or 'png' in fn or fn == 'jScrollPane.js':
            request.setHeader("Cache-Control", "max-age=290304000, public")
        else:
            request.setHeader("Cache-Control", "max-age=0, must-revalidate")#7200

        # ct = zope.contenttype.guess_content_type(fileForReading.name, fileForReading)[0]
        request.setHeader('Content-Encoding', 'gzip')

        if 'html' in self.type: # ct:
            #ct += ';charset=utf-8'
            self.type += ';charset=utf-8'
        request.setHeader('Content-Type', self.type)#ct)
        last_modified = self.getmtime()

        # do i need 304?
        if request.setLastModified(last_modified) is CACHED and fileForReading.name in _cached_statics and _cached_statics[fileForReading.name][0] == last_modified:
            return ''

        if fileForReading.name in _cached_statics and _cached_statics[fileForReading.name][0] == last_modified:
            return _cached_statics[fileForReading.name][1]
        else:
            d = threads.deferToThread(self.makeGzip, fileForReading, last_modified)
            d.addCallback(self.render_GSIPPED, request)
            return NOT_DONE_YET

    def makeGzip(self, fileForReading, last_modified):
        not_min = "js" in fileForReading.name and "min." not in fileForReading.name
        content = fileForReading.read()
        if not_min:
            content = jsmin(content)
        buff = StringIO()
        f = gzip.GzipFile(fileForReading.name,'wb',9, buff)

        fileForReading.close()

        f.write(content)
        f.close()

        buff.seek(0)
        gzipped = buff.read()
        buff.close()
        _cached_statics[fileForReading.name] = (last_modified, gzipped)
        return gzipped

    def render_GSIPPED(self, gzipped, request):
        request.write(gzipped)
        request.finish()

class Root(Resource):
    def __init__(self, host_url):
        Resource.__init__(self)
        self.static = CachedStatic(static_dir)
        self.static.indexNames = ['index.html']
        self.putChild('static',self.static)
        self.putChild('xml',XmlGetter())
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
        print "-------------------------------------"
        print u
        if ('http://' + self.host_url + '/' == u):
            return self.static.getChild(name, request)
        return self

from pc.secure import xml_source,xml_method, xml_login, xml_password
from lxml import etree

class XmlGetter(Resource):
    def pr(self, res):
        log.startLogging(sys.stdout)
        src = base64.decodestring(res)
        sio = StringIO(src)
        gz = gzip.GzipFile(fileobj=sio)
        f = open('d:\\Users\\agn\\xmlrpc.txt', 'w')
        f.write(gz.read())
        f.close()
        
        
    def render_GET(self, request):
        proxy = Proxy(xml_source)
        proxy.callRemote(xml_method, xml_login, xml_password).addCallbacks(self.pr, self.pr)
        return "ok"

