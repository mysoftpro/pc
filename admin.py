# -*- coding: utf-8 -*-
from twisted.internet import reactor, defer
from twisted.web.server import NOT_DONE_YET
import os
from pc.couch import couch, designID
import simplejson
from datetime import date
from pc.models import noComponentFactory,parts_names,parts,\
    BUILD_PRICE,INSTALLING_PRICE,DVD_PRICE,\
    Model, notes, case,case_exclusive,noChoicesYet,fillChoices, psu as power_catalog
from pc.catalog import getNewImage, getNewDescription
from twisted.web import proxy
from lxml import etree
from pc.root import CachedStatic, static_dir, HandlerAndName, Computer
from pc.simple_pages import parts_aliases
from twisted.web.guard import HTTPAuthSessionWrapper, DigestCredentialFactory
from twisted.cred.checkers import FilePasswordDB
from twisted.cred.portal import IRealm, Portal
from zope.interface import implements
from twisted.web.resource import IResource
from pc.common import MIMETypeJSON, forceCond
from twisted.web.static import File
from twisted.web.resource import Resource
from copy import deepcopy

realm_dir = os.path.join(os.path.dirname(__file__), 'realm')


def updateOriginalModelPrices():
    def update(res):
        for row in res['rows']:
            model = row['doc']
            model['original_prices'] = {}
            from pc import models
            for name,code in model['items'].items():
                if type(code) is list:
                    code = code[0]
                if code in models.gChoices_flatten:
                    component = models.gChoices_flatten[code]
                    model['original_prices'].update({code:component['price']})
                else:
                    model['original_prices'].update({code:99})
            couch.saveDoc(model)
    d = couch.openView(designID,'models',include_docs=True,stale=False)
    d.addCallback(update)




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
	self.putChild('couch',proxy.ReverseProxyResource('127.0.0.1', 5984,'', reactor=reactor))
	self.putChild('findorder', FindOrder())
	self.putChild('storeorder', StoreOrder())
	self.putChild('storemodel', StoreModel())
	self.putChild('mothers', Mothers())
	self.putChild('store_mother', StoreMother())
	self.putChild('store_promo', StorePromo())
	self.putChild('procs', Procs())
	self.putChild('store_proc', StoreProc())
	self.putChild('videos', Videos())
	self.putChild('store_video', StoreVideo())
	self.putChild('notebooks', NoteBooks())
	self.putChild('store_note', StoreNote())
	self.putChild('warranty', WarrantyFill())
	self.putChild('show_how', ShowHow())
	self.putChild('edit_how', EditHow())
	self.putChild('comet', AdminComet())
	self.putChild('acceptComet', AcceptComet())
	self.putChild('session', SessionGetter())
	self.putChild('promo', Promo())
	self.putChild('wit_for_mapping', WitForMapping())
	self.putChild('new_for_mapping', NewForMapping())
	self.putChild('store_wit_new_map',StoreWitNewMap())
	self.putChild('delete_wit_new_map',DeleteWitNewMap())

	self.putChild('get_new_descriptions',GetNewDescriptions())
        self.putChild('get_desc_from_new',GetDescFromNew())
        self.putChild('store_new_desc',StoreNewDesc())

        self.putChild('psus', Psus())
	self.putChild('store_psu', StorePsu())
        self.putChild('evolve', Evolve())

        self.putChild('store_description', StoreDescription())


    def render_GET(self, request):
	return self.static.getChild('index.html', request).render(request)

    def getChild(self, name, request):
	if 'html' in name or 'js' in name or 'jpg' in name:
	    return self.static.getChild(name, request)
	return self



class StoreDescription(Resource):
    def fail(self, fail, msg, request):
        request.write(str(fail))
        request.write(str(msg))
        request.finish()

    def finish(self, res, request):
        request.write(str(res['rev']))
        request.finish()

    def store(self, doc, description, request):
        if 'description' in doc:
            doc['description']['comments'] = description
        else:
            doc['description'] = {'comments':description,'imgs':[]}
        d = couch.saveDoc(doc)
        d.addErrback(self.fail, 'fail in store', request)
        d.addCallback(self.finish, request)

    def render_POST(self, request):
        _id = request.args.get('_id', [None])[0]
        description = request.args.get('descr', [None])[0]
        if _id is None or description is None:
            return 'fail params'
        d = couch.openDoc(_id)
        d.addCallback(self.store, description, request)
        d.addErrback(self.fail, 'fail in open', request)
        return NOT_DONE_YET

class Promo(Resource):

    def finish(self, components, promo, request):
	components = [c for c in components if c[0]]
	request.write(simplejson.dumps({'components':components, 'promo':promo}))
	request.finish()

    def fillComponents(self, promo, request):
	components = []
	for c in promo['components']:
	    components.append(couch.openDoc(c['code']))
	li = defer.DeferredList(components)
	li.addCallback(self.finish, promo, request)
	return li

    @MIMETypeJSON
    def render_GET(self, request):
	key = request.args.get('key',[None])[0]
	if key is None: return "ok"
	promo = couch.openDoc(key)
	promo.addCallback(self.fillComponents, request)
	return NOT_DONE_YET


class Mothers(Resource):
    def finish(self, result, request):	
	request.write(simplejson.dumps(result))
	request.finish()

    @MIMETypeJSON
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
	request.write(simplejson.dumps(result))
	request.finish()
    @MIMETypeJSON
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



class Procs(Resource):
    def finish(self, result, request):
	request.write(simplejson.dumps(result))
	request.finish()

    @MIMETypeJSON
    def render_GET(self, request):
	from pc import models
	defer.DeferredList([couch.openView(designID,
					   "catalogs",
					   include_docs=True,key=models.proc_1155, stale=False),
			    #.addCallback(lambda res:('LGA1155',res)),
			    couch.openView(designID,
					   'catalogs',
					   include_docs=True,key=models.proc_1156, stale=False),
			    # .addCallback(lambda res:('LGA1156',res)),
			    # couch.openView(designID,
			    #              'catalogs',
			    #              include_docs=True,key=proc_1366, stale=False)
			    #              .addCallback(lambda res:('LGA1366',res)),
			    couch.openView(designID,
					   'catalogs',
					   include_docs=True,key=models.proc_am23, stale=False),
			    #.addCallback(lambda res:('AM2 3',res)),
			    couch.openView(designID,
					   'catalogs',
					   include_docs=True,key=models.proc_775, stale=False),
			    #.addCallback(lambda res:('LGA755',res)),
			    couch.openView(designID,
					   'catalogs',
					   include_docs=True, key=models.proc_fm1, stale=False),
			    #.addCallback(lambda res: ("FM1",res))
			    ]).addCallback(self.finish, request)
	return NOT_DONE_YET



class NoteBooks(Resource):

    def finish(self, result, request):	
	request.write(simplejson.dumps(result))
	request.finish()

    @MIMETypeJSON
    def render_GET(self, request):
	asus_12 = ["7362","7404","7586"]
	asus_14 = ["7362","7404","7495"]
	asus_15 = ["7362","7404","7468"]
	asus_17 = ["7362","7404","7704"]
	couch.openView(designID,'catalogs',include_docs=True,stale=False,
			   keys = [asus_12,asus_14,asus_15,asus_17]).addCallback(self.finish, request)
	return NOT_DONE_YET





class FindOrder(Resource):

    def graceFull(self, fail, request):
	self.finish((((False, fail),),), request)


    def finish(self, result, request):
	# first level
	for li in result:
	    for tu in li:
		if not tu[0]:
		    request.write(simplejson.dumps({'fail':str(tu[1])}))
		    request.finish()
		    return
	request.write(simplejson.dumps(result))
	request.finish()


    def addComponents(self, model_user, _id):
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
		    doc['ourprice'] = Model.makePrice(doc)
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

        _model = Model(model_user[0][1])
	for k,v in model_user[0][1]['items'].items():
            component = wrap(_model.findComponent(k))
            if type(v) is list:
                component.addCallback(addCount(len(v)))
	    # component = None
	    # if v is not None:
	    #     try:
	    #         if type(v) is list:
	    #     	# component = couch.openDoc(v[0])
	    #     	# TODO! what if no component in choices?????????
	    #     	component = wrap(deepcopy(models.gChoices_flatten[v[0]]))
	    #     	component.addCallback(addCount(len(v)))
	    #         else:
	    #     	if not v.startswith('no'):
	    #     	    # component = couch.openDoc(v)
	    #     	    component = wrap(deepcopy(models.gChoices_flatten[v]))
	    #     	    component.addCallback(addCount(1))
	    #     	else:
	    #     	    component = wrap(noComponentFactory({}, k))
	    #     except KeyError:
            #         print "aheheheheheh"
	    #         component = wrap(noComponentFactory({'_id':v}, k))
	    # else:
	    #     component = wrap(noComponentFactory({}, k))
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
        def getUser(model):
	    d1 = couch.openDoc(model['author'])
	    mock = defer.Deferred()
	    mock.addCallback(lambda x: model)
	    mock.callback(None)
	    li = defer.DeferredList([mock,d1])
	    li.addCallback(self.addComponents, _id)
	    li.addCallback(self.finish, request)
	    return li
	d.addCallback(getUser)
	return d


    def getThree(self, result, request):
	model = None
	for r in result['rows']:
	    model = r['doc']
	    break
	d1 = couch.openDoc(model['author'])
	mock = defer.Deferred()
	mock.addCallback(lambda x: model)
	mock.callback(None)
	li = defer.DeferredList([mock,d1])
	li.addCallback(self.addComponents, model['_id'])
	li.addCallback(self.finish, request)
	return li

    @MIMETypeJSON
    def render_GET(self, request):
	_id = request.args.get('id')[0]
	if len(_id)>3:
	    order_d = couch.openDoc('order_'+_id)
            order_d.addCallback(self.finish, request)
	    # if no order -> get model            
	    order_d.addErrback(self.getModel, _id, request)
	    # if problem with the order -> finish any way
	    order_d.addErrback(self.graceFull, request)
	else:
	    d = couch.openView(designID, 'last_free', key=_id, include_docs=True)
	    d.addCallback(self.getThree, request)
	return NOT_DONE_YET

# REMEMBER! each order linked to model by id!
# somewhone make an order for several models will have some orders
class StoreOrder(Resource):
    def finish(self, order_res, model_rev, request):
	request.write(str(order_res['rev'])+'.'+str(model_rev))
	request.finish()

    def storeOrder(self, model_res, order, model, request):
        if model_res is not None:
            model['_rev'] = model_res['rev']
            order['model'] = model
	d = couch.saveDoc(order)
	d.addCallback(self.finish, model['_rev'], request)

    @MIMETypeJSON
    def render_POST(self, request):
	order = request.args.get('order')[0]
	jorder = simplejson.loads(order)
	jorder['date']=str(date.today()).split('-')
	model = jorder['model']
        if not 'processing' in model:
            model['processing'] = True
            d = couch.saveDoc(model)
            d.addCallback(self.storeOrder, jorder,model,request)
        else:
            d = defer.Deferred()
            d.addCallback(self.storeOrder, jorder,model,request)
            d.callback(None)
	return NOT_DONE_YET


class StorePromo(Resource):
    def finish(self, doc, request):
	request.write(str(doc['rev']))
	request.finish()

    @MIMETypeJSON
    def render_POST(self, request):
	promo = request.args.get('promo')[0]
	jpromo = simplejson.loads(promo)
	d = couch.saveDoc(jpromo)
	d.addCallback(self.finish, request)
	return NOT_DONE_YET




class StoreMother(Resource):
    def finish(self, doc, request):
	request.write(str(doc['rev']))
	request.finish()

    @MIMETypeJSON
    def render_POST(self, request):
	mother = request.args.get('mother')[0]
	jmother = simplejson.loads(mother)
	d = couch.saveDoc(jmother)
	d.addCallback(self.finish, request)
	return NOT_DONE_YET



class StoreVideo(Resource):
    def finish(self, doc, request):
	request.write(str(doc['rev']))
	request.finish()

    @MIMETypeJSON
    def render_POST(self, request):
	video = request.args.get('video')[0]
	jvideo = simplejson.loads(video)
	d = couch.saveDoc(jvideo)
	d.addCallback(self.finish, request)
	return NOT_DONE_YET


class StoreProc(Resource):

    
    def finish(self, doc, request):
	request.write(str(doc['rev']))
	request.finish()
    
    @MIMETypeJSON
    def render_POST(self, request):
	proc = request.args.get('proc')[0]
	jproc = simplejson.loads(proc)
	d = couch.saveDoc(jproc)
	d.addCallback(self.finish, request)
	return NOT_DONE_YET


class StoreNote(Resource):
    def finish(self, doc, request):
	request.write(str(doc['rev']))
	request.finish()

    @MIMETypeJSON
    def render_POST(self, request):
	note = request.args.get('note')[0]
	jnote = simplejson.loads(note)
	d = couch.saveDoc(jnote)
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
	d.addCallback(self.finish, request)
	return d

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
        child.hooks.update({'computer.html':HandlerAndName(Computer, name)})
	script = etree.Element('script')
	script.set('type','text/javascript')
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
            if not 'count' in c:
                c['count'] = 1
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
	request.write(simplejson.dumps(ob))
	request.finish()

    @MIMETypeJSON
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
	request.write(simplejson.dumps(res))
	request.finish()

    @MIMETypeJSON
    def render_POST(self,request):
	defs = []
	for name in parts_aliases.values():
	    defs.append(couch.openDoc(name[0]))
	li = defer.DeferredList(defs)
	li.addCallback(self.finish, request)
	return NOT_DONE_YET

class EditHow(Resource):

    def finish(self, res, request):
	request.write(simplejson.dumps(res))
	request.finish()

    @MIMETypeJSON
    def render_POST(self,request):
	doc = request.args.get('doc',[None])[0]
	d = couch.saveDoc(simplejson.loads(doc))
	d.addCallback(self.finish, request)
	return NOT_DONE_YET


class AdminComet(Resource):

    @MIMETypeJSON
    def render_GET(self, request):
	request.write(simplejson.dumps(globals()['_comet_users'].keys()))
	request.finish()


class AcceptComet(Resource):
    def render_GET(self, request):
	_id = request.args.get('id', [None])[0]
	if _id is not None and _id in globals()['_comet_users']:
	    globals()['_comet_users'][_id].write('ok')
	    globals()['_comet_users'][_id].finish()
	    globals()['_comet_users'].pop(_id)
	    return "ok"
	_clear = request.args.get('clear', [None])[0]
	if _clear is not None:
	    globals()['_comet_users'] = {}
	    return "ok"
	return "fail"

class SessionGetter(Resource):
    @MIMETypeJSON
    def render_GET(self, request):
	return simplejson.dumps({'Authorization':request.getHeader('authorization')})


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
	d = couch.openView(designID,"wit_codes", include_docs=True, stale=False)
	d.addCallback(self.clear)
	return "ok"


def clear_cache():
    # globals()['_cached_statics'] = {}
    # _dir = globals()['static_dir']
    from pc import root
    root._cached_statics = {}
    for f in os.listdir(root.static_dir):
	try:
	    os.utime(os.path.join(root.static_dir,f), None)
	except:
	    pass
    from pc import views
    views.no_component_added = False
    from pc import models
    models.gChoices = None
    models.gChoices_flatten = {}
    models.gWarning_sent = []
    d = models.fillChoices()
    d.addCallback(lambda x: updateOriginalModelPrices())



class NewForMapping(Resource):
    def finish(self, res, request):
        new_res = {'rows':[]}
        for r in res['rows']:
            if r['doc']['new_catalogs'] not in ['videos', 'procs', 'mothers']:
                continue
            new_res['rows'].append(r)
	request.write(simplejson.dumps(new_res))
	request.finish()

    @MIMETypeJSON
    def render_GET(self, request):
	d = couch.openView(designID, 'new_components', include_docs=True)
	d.addCallback(self.finish, request)
	return NOT_DONE_YET

class WitForMapping(Resource):

    def finish(self, res, request):
	request.write(simplejson.dumps(res))
	request.finish()

    @MIMETypeJSON
    def render_GET(self, request):
	import models
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
			       include_docs=True, key=models.mother_fm1, stale=False),
		# .addCallback(lambda res: ("FM1",res))

		couch.openView(designID,
			       "catalogs",
			       include_docs=True,key=models.proc_1155, stale=False),
		#.addCallback(lambda res:('LGA1155',res)),
		couch.openView(designID,
			       'catalogs',
			       include_docs=True,key=models.proc_1156, stale=False),
		couch.openView(designID,
			       'catalogs',
			       include_docs=True,key=models.proc_am23, stale=False),
		#.addCallback(lambda res:('AM2 3',res)),
		couch.openView(designID,
			       'catalogs',
			       include_docs=True,key=models.proc_775, stale=False),
		#.addCallback(lambda res:('LGA755',res)),
		couch.openView(designID,
			       'catalogs',
			       include_docs=True, key=models.proc_fm1, stale=False),
		#.addCallback(lambda res: ("FM1",res))
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

class StoreWitNewMap(Resource):

    def finish(self, res, request):
	if res[0][0] and res[1][0]:
	    request.write("ok")
	else:
	    request.write("fail")
	request.finish()

    def storeWi(self, doc, ne):
	doc['map_to_ne'] = ne
	return couch.saveDoc(doc)

    def storeNe(self, doc, wi):
	doc['map_to_wi'] = wi
        # destroy catalogs. it will need catalogs again!
        if 'catalogs' in doc:
            doc.pop('catalogs')
	return couch.saveDoc(doc)

    def render_GET(self, request):
	ne = request.args.get('ne')[0]
	wi = request.args.get('wi')[0]
	d1 = couch.openDoc(wi)
	d2 = couch.openDoc(ne)
	d1.addCallback(self.storeWi, ne)
	d2.addCallback(self.storeNe, wi)
	li = defer.DeferredList([d1,d2])
	li.addCallback(self.finish, request)
	return NOT_DONE_YET


class DeleteWitNewMap(Resource):

    def finish(self, res, request):
	if res[0][0] and res[1][0]:
	    request.write("ok")
	else:
	    request.write("fail")
	request.finish()

    def deleteWi(self, doc):
	if 'map_to_ne' in doc:
	    doc.pop('map_to_ne')
	return couch.saveDoc(doc)

    def deleteNe(self, doc):
	if 'map_to_wi' in doc:
	    doc.pop('map_to_wi')
	return couch.saveDoc(doc)

    def render_GET(self, request):
	ne = request.args.get('ne')[0]
	wi = request.args.get('wi')[0]
	d1 = couch.openDoc(wi)
	d2 = couch.openDoc(ne)
	d1.addCallback(self.deleteWi)
	d2.addCallback(self.deleteNe)
	li = defer.DeferredList([d1,d2])
	li.addCallback(self.finish, request)
	return NOT_DONE_YET


class GetNewDescriptions(Resource):

    def finish(self, res, request):
        request.write(simplejson.dumps(res))
        request.finish()

    @MIMETypeJSON
    def render_GET(self, request):
        key = request.args.get('key',[None])[0]        
        if key is None:
            d = couch.openView(designID, 'new_unique_components', include_docs=True)
        else:            
            d = couch.openView(designID, 'new_unique_components', include_docs=True, key=key)
        d.addCallback(self.finish, request)
        return NOT_DONE_YET

class GetDescFromNew(Resource):

    def finish(self, res, request):
        request.write(res)
        request.finish()

    @MIMETypeJSON
    def render_GET(self, request):
        link = request.args.get('link')[0]        
        d = getNewDescription(link)
        d.addCallback(self.finish, request)
        return NOT_DONE_YET


class StoreNewDesc(Resource):

    def finish(self, doc, desc, name, img, warranty, articul, catalogs):
        doc['description'] = {}
        doc['description'].update({'comments':desc})
        doc['description'].update({'name':name})
        #TODO get and store image!
        if len(warranty)>0:
            doc['warranty_type'] = warranty
        if len(articul)>0:
            doc['articul'] = articul.replace('\t','')
        if len(catalogs)>0:
            doc['catalogs'] = simplejson.loads(catalogs)
            doc['price'] = doc['us_price']
            doc['stock1'] = doc['new_stock']

        if len(img)>0:
            doc['description'].update({'imgs':[img]})
        else:
            doc['description'].update({'imgs':[]})

        d = couch.saveDoc(doc)
        if len(img)>0:
            d.addCallback(getNewImage, img)
        return d
            
    def render_POST(self, request):
        _id = request.args.get('id')[0]
        desc = request.args.get('desc')[0]
        img = request.args.get('img')[0]
        name = request.args.get('name')[0]
        warranty = request.args.get('warranty')[0]
        articul = request.args.get('articul')[0]
        catalogs = request.args.get('catalogs')[0]
        d = couch.openDoc(_id)
        d.addCallback(self.finish, desc, name, img, warranty, articul, catalogs)
        return "ok"



class Psus(Resource):
    def finish(self, result, request):	
	request.write(simplejson.dumps(result))
	request.finish()
    @MIMETypeJSON
    def render_GET(self, request):
        from pc import models
	defer.DeferredList([
		couch.openView(designID,
			       'catalogs',
			       include_docs=True, key=models.power, stale=False),
		]).addCallback(self.finish, request)
	return NOT_DONE_YET


class StorePsu(Resource):
    def finish(self, doc, request):
	request.write(str(doc['rev']))
	request.finish()

    @MIMETypeJSON
    def render_POST(self, request):
	psu = request.args.get('psu')[0]
	jpsu = simplejson.loads(psu)
	d = couch.saveDoc(jpsu)
	d.addCallback(self.finish, request)
	return NOT_DONE_YET


class Evolve(Resource):

    # def fillNote(self, note_ob, code, date):
    #     note_ob['items'] = {notes:code}
    #     note_ob['date'] = date
    #     couch.saveDoc(note_ob)

    # def evolve(self, res):
    #     import pc.models        
    #     for r in res['rows']:
    #         if not 'doc' in r:continue
    #         if r['doc'] is None:
    #             continue
    #         model = Model(r['doc'])            
    #         # found_case = model.findComponent(case)
    #         # if model.getCatalogsKey(found_case) == case_exclusive:
    #         if model.case.getCatalogsKey() == case_exclusive:
    #             if not model.isPromo:
    #                 r['doc']['items'].update({power_catalog:"13559"})# 600w Deluxe
    #                 if 'original_prices' in r['doc']:
    #                     r['doc']['original_prices'].update({"13559":32})
    #             else:
    #                 r['doc']['items'].update({power_catalog:"18244"})# 500w Deluxe
    #                 if 'original_prices' in r['doc']:
    #                     r['doc']['original_prices'].update({"18244":20})
    #         else:
    #             r['doc']['items'].update({power_catalog:"no"+power_catalog})# psu is embeded in case
    #         couch.saveDoc(r['doc'])

    # def movePromos(self, res, promos_ids):
    #     to_save = {}
    #     for r in res['rows']:
    #         if 'doc' not in r or r['doc'] is None:continue
    #         new_models = []
    #         promos = []
    #         for i in r['doc']['models']:
    #             if i not in promos_ids:
    #                 new_models.append(i)
    #             else:
    #                 promos.append(i)
    #         r['doc']['models'] = new_models
    #         r['doc']['promos'] = promos
    #         if not r['doc']['_id'] in to_save:
    #             to_save.update({r['doc']['_id']:r['doc']})
    #     for v in to_save.values():
    #         couch.saveDoc(v)
        

    # def getUsers(self, res):
    #     rows=  res['rows']
    #     promos = [r['doc'] for r in rows if 'doc' in r and r['doc'] is not None\
    #                   and 'promo' in r['doc'] and r['doc']['promo']]
    #     d = couch.listDoc(keys=[doc['author'] for doc in promos], include_docs=True)
    #     d.addCallback(self.movePromos, [doc['_id'] for doc in promos])
    #     return d

    def fixOriginalPrices(self, res):
        for r in res['rows']:
            if 'original_prices' in r['doc']:
                new_prices= {}
                procced = False
                for k,v in r['doc']['original_prices'].items():
                    if type(v) is int or type(v) is float:
                        procced = True
                        break
                    else:
                        print r['doc']['_id']
                if procced:continue
                        

    @forceCond(noChoicesYet, fillChoices)
    def render_GET(self, request):
        d = couch.openView(designID,'user_models', include_docs=True)
        d.addCallback(self.fixOriginalPrices)
        return "ok"
