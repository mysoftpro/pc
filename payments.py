# -*- coding: utf-8 -*-
from twisted.web.resource import Resource
from pc.secure import do_key
import hashlib
from lxml import etree
from copy import deepcopy
from twisted.web.server import NOT_DONE_YET
from pc.couch import couch, designID
from twisted.internet import reactor, defer
from pc.mail import send_email
# http://www.onlinedengi.ru/wmpaycheck.php?project=867&amount=5&nickname=187e61f8&mode_type=60&source=buildpc.ru&order_id=187e70d0
# mode_type now is 108
# http://www.onlinedengi.ru/wmpaycheck.php?project=867&amount=5&nickname=2fafbb4c&mode_type=108&source=buildpc.ru&order_id=2fb0465c
# http://www.onlinedengi.ru/wmpaycheck.php?project=867&amount=5&nickname=2fafbb4c&mode_type=108&source=buildpc.ru&order_id=3cf88928 - good
class DOValidateUser(Resource):
    def __init__(self):
        self.xml = etree.XML('<result></result>')
        code = etree.Element('code')
        self.xml.append(code)

    def render_POST(self, request):
        userid = request.args.get('userid',[None])[0]
        userid_extra = request.args.get('userid_extra',[None])[0]
        key = request.args.get('key',[None])[0]
        ha = hashlib.md5()
        ha.update('0')
        if userid is not None:
            ha.update(userid)
        ha.update('0')
        ha.update(do_key)
        di = ha.hexdigest()
        answer = deepcopy(self.xml)

        if key is not None and di == key:
            answer.find('code').text = 'YES'
        else:
            answer.find('code').text = 'NO'

        return etree.tostring(answer, encoding='utf-8', xml_declaration=True)

class DONotifyPayment(Resource):

    def __init__(self):
        self.xml = etree.XML('<result></result>')
        id = etree.Element('id')
        code = etree.Element('code')
        comment = etree.Element('comment')
        # course = etree.Element('course')
        self.xml.append(id)
        self.xml.append(code)
        self.xml.append(comment)
        # self.xml.append(course)


    def finish(self, user_doc, answer, request):
        request.setHeader('Content-Type', 'text/xml;charset=utf-8')
        request.write(etree.tostring(answer, encoding='utf-8', xml_declaration=True))
        request.finish()

    def fail(self, fail, answer, request):
        answer.find('comment').text = str(fail)
        answer.find('code').text = 'NO'
        request.setHeader('Content-Type', 'text/xml;charset=utf-8')
        request.write(etree.tostring(answer, encoding='utf-8', xml_declaration=True))
        request.finish()

    # user['payments']= {'their_id':['our_id']}--> {'12345':['dabsd','db123''}]}
    def storePayment(self, payment_user, raw_payment, answer, request):
        if payment_user[0][0] and payment_user[1][0]:

            _payment = payment_user[1][1]
            _user = payment_user[0][1]
            # has payments
            if 'payments' in _user:
                stored = False
                for their_id,li in _user['payments'].items():
                    # same payment again
                    if their_id == raw_payment['paymentid']:
                        li.append(_payment['id'])
                        stored = True
                        break
                # new payment
                if not stored:
                    _user['payments'].update({raw_payment['paymentid']:[_payment['id']]})
            else:
                _user['payments'] = {raw_payment['paymentid']:[_payment['id']]}
            d = couch.saveDoc(_user)
            answer.find('code').text = 'YES'
            answer.find('id').text = _payment['id']
            d.addCallback(self.finish, answer, request)
            send_email('admin@buildpc.ru',
                       u'Совершен платеж',
                       _payment['id']+' '+_user['_id'],
                       sender=u'Компьютерный магазин <inbox@buildpc.ru>')
            return d
        else:
            answer.find('code').text = 'NO'
            # payment is stored, but no user
            if payment_user[1][0]:
                answer.find('id').text = payment_user[1][1]['id']
                answer.find('comment').text = u'No such user '+raw_payment['userid']
                d = defer.Deferred()
                d.addCallback(self.finish, answer, request)
                d.callback(None)
                return d
            else:                
                answer.find('comment').text = u'Cant store payment '+raw_payment['paymentid']
                d = defer.Deferred()
                d.addCallback(self.finish, answer, request)
                d.callback(None)
                return d


# curl -X POST 'localhost/do_notify_payment?amount=1&userid=2&paymentid=3&key=b3246e84884cd7bf732d1f5876b771d6'

    def render_POST(self, request):
        # userid_extra = request.args.get('userid_extra',[None])[0]
        amount = request.args.get('amount',[None])[0]
        userid = request.args.get('userid',[None])[0]
        userid_extra = request.args.get('userid_extra',[None])[0]
        paymentid = request.args.get('paymentid',[None])[0]
        key = request.args.get('key',[None])[0]
        paymode = request.args.get('paymode',[None])[0]
        orderid = request.args.get('orderid',[None])[0]
        serverid = request.args.get('serverid',[None])[0]

        ha = hashlib.md5()
        def up(some):
            if some is None: return
            ha.update(some)
        # amount + userid + paymentid + секретный ключ произвольного вида (до 35 символов).
        up(amount)
        up(userid)
        up(paymentid)
        up(do_key)

        di = ha.hexdigest()

        answer = deepcopy(self.xml)

        if key is not None and di == key:
            payment = {'userid':userid,'userid_extra':userid_extra,'paymentid':paymentid,'key':key,
                       'paymode':paymode,'orderid':orderid,'serverid':serverid,'amount':amount,
                       'type':'do_payment'}
            d = couch.openDoc(userid)
            d1 = couch.saveDoc(payment)
            li = defer.DeferredList([d,d1])
            li.addCallback(self.storePayment,payment,answer,request)
            li.addErrback(self.fail, answer, request)
            return NOT_DONE_YET
        else:
            answer.find('code').text = 'No'
            answer.find('comment').text = u'Invalid key'
            return etree.tostring(answer, encoding='utf-8', xml_declaration=True)
