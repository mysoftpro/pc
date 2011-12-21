# -*- coding: utf-8 -*-
from pc.twsited_client_11_1 import Agent, Headers11
from twisted.internet.protocol import Protocol
from cStringIO import StringIO
import gzip
from twisted.web.resource import Resource
import simplejson
from pc.couch import couch, designID
from twisted.internet import reactor, defer
from twisted.web.server import NOT_DONE_YET
from pc import base36
from datetime import datetime
from pc.common import addCookies
import hashlib
from pc.secure import mail_app_id,mail_secret_key, vk_app_id, vk_secret_key, goog_client_id, goog_secret
from twisted.internet.defer import succeed
from twisted.web.iweb import IBodyProducer
from zope.interface import implements
from urllib import unquote_plus, quote_plus

class LineReceiver(Protocol):
    def __init__(self, finished, encoding):
	self.finished = finished
	self.file = StringIO()
	self.gzip = False
	if "gzip" == encoding:
	    self.gzip = True

    def dataReceived(self, bytes):
	self.file.write(bytes)

    def ungzip(self):
	self.file.seek(0)
	gzipper = gzip.GzipFile(fileobj=self.file)
	self.file = StringIO(gzipper.read())
	return self.file

    def connectionLost(self, reason):
	# print self.file.tell()
	# so. the file is at the end, and it tell() me how much bytes it has!
	if self.gzip:
	    self.ungzip()
	self.file.seek(0)
	self.finished.callback(self.file)


class PostProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
	self.body = str(body)
	self.length = len(self.body)

    def startProducing(self, consumer):
	consumer.write(self.body)
	return succeed(None)

    def pauseProducing(self):
	pass

    def stopProducing(self):
	pass




class OAuth(Resource):
    def __init__(self):
	Resource.__init__(self)
	self.auths = {'mail':self.mail,'vkontakt':self.vkontakt,'facebook':self.facebook,
		      'goog':self.goog, 'yandex':self.yandex}


    # TODO! decorate this method @json_response
    def prepRequest(self, request):
	request.setHeader('Content-Type', 'application/json')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")


    def render_GET(self, request):
	pr = request.args.get('pr', [None])[0]
	access_token = request.args.get('access_token', [None])[0]
	code = request.args.get('code', [None])[0]
        
	if pr is None or (access_token is None and code is None) or pr not in self.auths:
	    return "fail"
	pc_user = request.getCookie('pc_user')
	d = couch.openDoc(pc_user)
	d.addCallback(self.auths[pr], access_token, code, request)
	def new_user(fail):
	    return self.auths[pr]( {'_id':pc_user,'models':[],'pc_key':base36.gen_id(), 'new':True},
			    access_token, code, request)
	d.addErrback(new_user)
	return NOT_DONE_YET


    def addNewSockUser(self, received_soc_user_ob, user_doc):
	if 'new' in user_doc:
	    # there are no user in db
	    user_doc.pop('new')
	    user_doc['soc_users'] = [received_soc_user_ob]
	    # print "save new user_doc!"
	    # print user_doc
	    couch.saveDoc(user_doc)
	else:
	    if 'soc_users' in user_doc:
		# user was authorized before by soc network
		if received_soc_user_ob['uid'] in [ob['uid'] for ob in user_doc['soc_users']]:
		    # print "pass"
		    pass
		else:
		    # just append new soc network to existing user
		    user_doc['soc_users'].append(received_soc_user_ob)
		    # print "save OLD user_doc 1!"
		    # print user_doc
		    couch.saveDoc(user_doc)
	    else:
		# just add soc user to previously stored user
		user_doc['soc_users'] = [received_soc_user_ob]
		couch.saveDoc(user_doc)
		# print "save OLD user_doc 2!"
		# print user_doc


    def updateModelsAuthor(self, res, user_doc):
	for r in res['rows']:
	    if r['doc']['author'] != user_doc['_id']:
		r['doc']['author'] = user_doc['_id']
		couch.saveDoc(r['doc'])




    def installPreviousUser(self, soc_user_doc, request):
	in_cart = len(soc_user_doc['models'])
	if 'notebooks' in soc_user_doc:
	    in_cart+=len(soc_user_doc['notebooks'].keys())
	    addCookies(request, {'pc_user':soc_user_doc['_id'],
				 'pc_key':soc_user_doc['pc_key'],
				 'pc_cart':str(in_cart)})

	d = couch.listDoc(keys=soc_user_doc['models'], include_docs=True)
	d.addCallback(self.updateModelsAuthor, soc_user_doc)

    def mergeUsers(self, stored_soc_user_doc_res, received_soc_user_ob, user_doc, request):
	"""
	3 cases

	2. has user_doc and pc_cookie match with that doc _id
	   its ok. just write user_ob to request and thats all
	3. has user_doc and pc_cookie DO NOT match with that doc _id
	   write user_ob to request. install found user_doc _id and pc_key
	   to request cookies. return request. separattely merge the carts
	betwwen present pc_cookie and user_doc to user_doc!!!!!!!!!!!!!!!!
	"""
	rows = stored_soc_user_doc_res['rows']
	clean_rows = [row['doc'] for row in rows if 'doc' in row and row['doc'] is not None]
	if len(clean_rows) == 0:
	    # 1. no answer from view. -> new soc user. store soc_user in user_doc
	    self.addNewSockUser(received_soc_user_ob, user_doc)
	else:
	    # just take first doc! oldest one and merge all to it
	    soc_user_doc = sorted(clean_rows, lambda x,y: int(x['_id'], 16)-int(y['_id'],16))[0]
	    if soc_user_doc['_id'] == user_doc['_id']:
		# its the same doc. all ok.
		# print "cookies are the same for this user and authorized user!"
		pass
	    else:
		# i have 2 different docs here.
		if 'new' in user_doc:
		    # no merge required, because user_doc is not stored yet
		    self.installPreviousUser(soc_user_doc, request)
		    # print "no merge required, because user_doc is not stored yet"
		else:
		    # merge soc user and previously stored user
		    for k,v in user_doc.items():
			if k in ['_id','_rev','pc_key']: continue
			if k not in soc_user_doc:
			    soc_user_doc[k] = v
			    continue
			else:
			    if type(v) is list:
				for el in v:
				    if el in soc_user_doc[k]:continue
				    soc_user_doc[k].append(el)
			    # ??? what about other types? i do not no yet. ATTENTION!
		    if 'merged_docs' in soc_user_doc:
			if user_doc['_id'] not in soc_user_doc['merged_docs']:
			    soc_user_doc['merged_docs'].append(user_doc['_id'])
		    else:
			soc_user_doc['merged_docs'] = [user_doc['_id']]
		    couch.saveDoc(soc_user_doc)
		    # print "SAVE MERGED doc"
		    # print soc_user_doc
		    # print user_doc
		    self.installPreviousUser(soc_user_doc, request)
	self.prepRequest(request)
	request.write(simplejson.dumps(received_soc_user_ob))
	request.finish()



    def getOauthAnswer(self, response, further_d):
	enc = ''
	for h in response.headers.getAllRawHeaders():
	    if h[0] == 'Content-Encoding':
		enc = h[1][0]
		break
	response.deliverBody(LineReceiver(further_d, enc))


    def parseGoog(self, f, user_doc, request):
        answer = simplejson.loads(f.read())
        soc_user_ob = {}
	soc_user_ob['uid'] = 'go'+answer['id']
        soc_user_ob['first_name'] = answer['given_name']
        soc_user_ob['last_name'] = answer['family_name']
	d = couch.openView(designID, 'soc_users', key=soc_user_ob['uid'], include_docs=True)
	d.addCallback(self.mergeUsers, soc_user_ob, user_doc, request)
	f.close()


    def getGoogAccessToken(self, f, user_doc, request):
	""""""
	answer = simplejson.loads(f.read())
	agent = Agent(reactor)
	url = 'https://www.googleapis.com/oauth2/v1/userinfo?access_token='+answer['access_token']
	request_d = agent.request('GET', str(url),Headers11({}),None)
	d = defer.Deferred()
	d.addCallback(self.parseGoog, user_doc, request)
	request_d.addCallback(self.getOauthAnswer, d)
	return request_d
	f.close()


    def goog(self, user_doc, access_token, code, request):
	# soc_user_id = request.args.get('user_id')[0]
	agent = Agent(reactor)
	body = 'code=%s&client_id=%s&client_secret=%s&grant_type=authorization_code&redirect_uri=%s' % (code, goog_client_id, goog_secret, quote_plus('http://buildpc.ru?pr=goog'))
	request_d = agent.request('POST',
				  'https://accounts.google.com/o/oauth2/token',
				  Headers11({'Content-Type':['application/x-www-form-urlencoded']}),PostProducer(body))
	d = defer.Deferred()
	d.addCallback(self.getGoogAccessToken, user_doc, request)
	request_d.addCallback(self.getOauthAnswer, d)
	return request_d




    def parseVkontakt(self, f, user_doc, request):
	answer = simplejson.loads(f.read())
	f.close()
	soc_user_ob = answer['response'][0]
	soc_user_ob['uid'] = 'vk'+str(soc_user_ob['uid'])
	# ok. now i have user_ob from soc network and user_doc
	# it need to call some view with the 'vk'+user_ob[uuid]
	d = couch.openView(designID, 'soc_users', key=soc_user_ob['uid'], include_docs=True)
	d.addCallback(self.mergeUsers, soc_user_ob, user_doc, request)


    def getVkontaktAccessToken(self, f, user_doc, request):
        src = f.read()
	answer = simplejson.loads(src)
	f.close()
        url = 'https://api.vkontakte.ru/method/getProfiles?uid=%s&access_token=%s' %\
	    (answer['user_id'],answer['access_token'])	
	agent = Agent(reactor)
	request_d = agent.request('GET', str(url),Headers11({}),None)
	d = defer.Deferred()
	d.addCallback(self.parseVkontakt, user_doc, request)
	request_d.addCallback(self.getOauthAnswer, d)
	return request_d

    def vkontakt(self, user_doc, access_token, code, request):
	# soc_user_id = request.args.get('user_id')[0]
	agent = Agent(reactor)
	request_d = agent.request('GET', 'https://api.vkontakte.ru/oauth/access_token?client_id=%s&client_secret=%s&code=%s' % (vk_app_id, vk_secret_key, code),Headers11({}),None)
	d = defer.Deferred()
	d.addCallback(self.getVkontaktAccessToken, user_doc, request)
	request_d.addCallback(self.getOauthAnswer, d)
	return request_d



    def parseMail(self, f, user_doc, request):
	answer = simplejson.loads(f.read())
	f.close()
	soc_user_ob = {'uid':answer[0]['uid'], 'first_name':answer[0]['first_name'],'last_name':answer[0]['last_name']}
	soc_user_ob['uid'] = 'ma'+str(soc_user_ob['uid'])
	# ok. now i have user_ob from soc network and user_doc
	# it need to call some view with the 'vk'+user_ob[uuid]
	d = couch.openView(designID, 'soc_users', key=soc_user_ob['uid'], include_docs=True)
	d.addCallback(self.mergeUsers, soc_user_ob, user_doc, request)


    def mail(self, user_doc, access_token, code, request):
	agent = Agent(reactor)
	ha = hashlib.md5()
	ha.update('app_id=%smethod=users.getInfosecure=1session_key=%s' % (mail_app_id,access_token))
	ha.update(mail_secret_key)
	sig = ha.hexdigest()
	request_d = agent.request('GET', 'http://www.appsmail.ru/platform/api?method=users.getInfo&app_id=%s&session_key=%s&secure=1&sig=%s' % (mail_app_id, access_token, sig),Headers11({}),None)
	d = defer.Deferred()
	d.addCallback(self.parseMail, user_doc, request)
	request_d.addCallback(self.getOauthAnswer, d)
	return request_d



    def parseFacebook(self, f, user_doc, request):
	answer = simplejson.loads(f.read())
	f.close()
	soc_user_ob = {'uid':answer['id'],
		       'first_name':answer['first_name'],
		       'last_name':answer['last_name']}
	soc_user_ob['uid'] = 'fb'+str(soc_user_ob['uid'])
	# ok. now i have user_ob from soc network and user_doc
	# it need to call some view with the 'vk'+user_ob[uuid]
	d = couch.openView(designID, 'soc_users', key=soc_user_ob['uid'], include_docs=True)
	d.addCallback(self.mergeUsers, soc_user_ob, user_doc, request)


    def facebook(self, user_doc, access_token, code, request):
	agent = Agent(reactor)
	request_d = agent.request('GET', 'https://graph.facebook.com/me?access_token=%s' % access_token,Headers11({}),None)
	d = defer.Deferred()
	d.addCallback(self.parseFacebook, user_doc, request)
	request_d.addCallback(self.getOauthAnswer, d)
	return request_d


    def yandex(self, user_doc, access_token, code, request):
        soc_user_ob = globals()['PASSED_USERS'].pop(request.getCookie('pc_user'))
        d = couch.openView(designID, 'soc_users', key=soc_user_ob['uid'], include_docs=True)
	d.addCallback(self.mergeUsers, soc_user_ob, user_doc, request)
        return d



class TestRequest(object):

    def setHeader(self, *args, **kwargs):
	pass

    def write(self, some):
	print "write to request!"
	print some

    def addCookie(self, *args, **kwargs):
	print "adding cookie"
	print args
	print kwargs

    def finish(self):
	print "request finished!"

if __name__ == '__main__':
    res = OAuth()
    print "______________________________"
    user_doc = {'_id':'pc_user','models':[],'pc_key':base36.gen_id(), 'new':True}
    received_soc_user = {'uid':'uid', 'first_name':'first_name', 'last_name':'last_name'}
    stored_soc_user_doc_res = {'rows':[]}
    res.mergeUsers(stored_soc_user_doc_res, received_soc_user, user_doc, TestRequest())

    print "______________________________"
    user_doc = {'_id':'pc_user','models':[],'pc_key':base36.gen_id()}
    res.mergeUsers(stored_soc_user_doc_res, received_soc_user, user_doc, TestRequest())

    print "______________________________"
    user_doc = {'_id':'pc_user','models':[],'pc_key':base36.gen_id(), 'soc_users':[{'uid':'best'}]}
    res.mergeUsers(stored_soc_user_doc_res, received_soc_user, user_doc, TestRequest())

    print "______________________________"
    user_doc = {'_id':'pc_user','models':[],'pc_key':base36.gen_id(), 'soc_users':[{'uid':'uid'}]}
    res.mergeUsers(stored_soc_user_doc_res, received_soc_user, user_doc, TestRequest())

    print ".."

    print "______________________________"
    user_doc = {'_id':'pc_user','models':[],'pc_key':base36.gen_id(), 'new':True}
    received_soc_user = {'uid':'uid', 'first_name':'first_name', 'last_name':'last_name'}
    stored_soc_user_doc_res = {'rows':[{'doc':{'_id':'pc_user','models':[],'pc_key':base36.gen_id()}}]}
    res.mergeUsers(stored_soc_user_doc_res, received_soc_user, user_doc, TestRequest())

    print "______________________________"
    stored_soc_user_doc_res = {'rows':[{'doc':{'_id':'some_id','models':[],'pc_key':base36.gen_id()}}]}
    res.mergeUsers(stored_soc_user_doc_res, received_soc_user, user_doc, TestRequest())

    print "______________________________"
    user_doc = {'_id':'pc_user','models':['1','2'],'pc_key':base36.gen_id()}
    stored_soc_user_doc_res = {'rows':[{'doc':{'_id':'some_id','models':['3','4'],'pc_key':base36.gen_id()}}]}
    res.mergeUsers(stored_soc_user_doc_res, received_soc_user, user_doc, TestRequest())

    print "______________________________"
    payments = [{"37336240": ["e27c8af05d7b1b2a3af83cfed01fa76c"]}]
    payments1 = [{"37336240": ["e27c8af05d7b1b2a3af83cfed01fa76c"]},{"1111": ["2222"]}]
    received_soc_user = {'uid':'uid', 'first_name':'first_name', 'last_name':'last_name'}
    user_doc = {'_id':'pc_user','models':['1','2'],'pc_key':base36.gen_id(), 'payments':payments}
    stored_soc_user_doc_res = {'rows':[{'doc':{'_id':'some_id','models':['3','4'],'pc_key':base36.gen_id(), 'payments':payments1}}]}
    res.mergeUsers(stored_soc_user_doc_res, received_soc_user, user_doc, TestRequest())




import tempfile
from openid.consumer.consumer import Consumer, SUCCESS, DiscoveryFailure
from openid.store.filestore import FileOpenIDStore
from openid.extensions import ax

STORAGE = FileOpenIDStore(tempfile.gettempdir())

ROOT = 'http://localhost'
RETURN_TO = ROOT+'/openid'
AXINFO = {
    'email': 'http://axschema.org/contact/email',
    'nickname': 'http://axschema.org/namePerson/friendly',
    'namePerson':'http://axschema.org/namePerson'
    }
REDIRECTED_USERS = {}
PASSED_USERS = {}

class OpenId(Resource):

    def render_GET(self, request):
        janrain_nonce = request.args.get('janrain_nonce', [None])[0]
        if janrain_nonce is not None:
            cookie = request.getCookie('pc_user')
            if not cookie in globals()['REDIRECTED_USERS']:
                request.redirect('http://buildpc.ru')
                return ""
            consumer = Consumer({}, STORAGE)
            args = dict((k,unicode(v[0], 'utf-8')) for k,v in request.args.items())

            info = consumer.complete(args, RETURN_TO)
            # Если аутентификация не удалась или отменена            
            # Получение данных пользователя при успешной аутентификации
            if info.status != SUCCESS:
                request.redirect('http://buildpc.ru')
                return ""
            
            ax_info = ax.FetchResponse.fromSuccessResponse(info) or ax.FetchResponse()
            user_data = {
                'uid': info.identity_url,
                'first_name': ax_info.getSingle(AXINFO['namePerson']),
                'last_name': '',                
            }
            globals()['PASSED_USERS'].update({cookie:user_data})
            request.redirect(globals()['REDIRECTED_USERS'].pop(cookie).split('?')[0]\
                                 +'?pr=yandex&code='+cookie)
            return ""
            
        # Далее — выборка существующего или регистрация нового пользователя
        else:
            backUrl = request.args.get('backurl', [None])[0]
            globals()['REDIRECTED_USERS'].update({request.getCookie('pc_user'):backUrl})
            # provider = request.get('provider', [None])[0]            
            # url = openid_request.redirectURL(ROOT, ROOT)
            
            # Короткие названия для ключей необходимых данных о пользователе.
            # Список доступных данных см. в разделе Дополнительные данные о пользователе
            
            consumer = Consumer({}, STORAGE)
            openid_request = consumer.begin('http://www.yandex.ru/')

            # Запрос дополнительной информации о пользователе
            # Поля, указанные с ключом required, на сайте Яндекса отображаются как обязательные
            # (незаданные значения подсвечиваются красным цветом)
            ax_request = ax.FetchRequest()
            # ax_request.add(ax.AttrInfo(AXINFO['email'], required=True))
            # ax_request.add(ax.AttrInfo(AXINFO['nickname']))
            ax_request.add(ax.AttrInfo(AXINFO['namePerson'], required=True))
            openid_request.addExtension(ax_request)
            url = openid_request.redirectURL(ROOT, RETURN_TO)
            request.redirect(url)
            return ""            
