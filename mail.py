# -*- coding: utf-8 -*-

from email.Header import Header
from email.Utils import parseaddr, formataddr
from twisted.mail.smtp import ESMTPSenderFactory
from urllib import unquote_plus
from pc.secure import mailpassword
import re
from string import Template
from email.MIMEText import MIMEText
from email.mime.multipart import MIMEMultipart
from twisted.web.server import NOT_DONE_YET
from twisted.web.resource import Resource

from cStringIO import StringIO
from twisted.internet import reactor, defer

class Sender(Resource):
    # def end(self, res, request):
    #     request.write("ok")
    #     request.finish()

    # def fail(self, res, request):
    #     request.write("fuck")
    #     request.finish()

    # details_template = Template("""
    #   <h1>$subject</h1>
    #   <p><a href="$url">$url</a></p>
    #   <p>$text</p>
    #   <table>$baseparams</table>
    #   <table>$rows</table>
    # """)

    # details_row_template = Template("""
    #     <tr><td>$name</td><td>$value</td>
    # """)
    # def sendDetails1(self, doc, request, recipient, url):
    #     rows = []
    #     for name,value in doc['params'].items():
    #         rows.append(self.details_row_template.substitute({'name':name,'value':value}))                        
        
    #     base_params =  []
    #     date = doc['date']
    #     date.reverse()
    #     base_params.append(self.details_row_template.substitute({'name':u'цена',
    #                                                              'value':u'<strong>' + doc['price'] + u'</strong>'}))
    #     base_params.append(self.details_row_template.substitute({'name':u'телефон',
    #                                                              'value':u'<strong>' + doc['phone'] + u'</strong>'}))
    #     base_params.append(self.details_row_template.substitute({'name':u'дата', 'value':u'.'.join(date)}))

    #     body = self.details_template.substitute({'subject':doc['subj'], 'url':url,
    #                                              'text':doc['text'],
    #                                              'baseparams':u''.join(base_params),
    #                                              'rows':u''.join(rows)
    #                                              })
    #     d = send_email(recipient, u'Объявление', body)
    #     d.addCallback(self.end, request)
    #     return d


    # favorites_template = Template(u"""<p><table><tr><td>$subj</td></tr>
    #                                   <tr><td>$body</td></tr>
    #                                   <tr><td>цена: <strong>$price</strong></td><tr>
    #                                   <tr><td>телефон: <strong>$phone</strong></td><tr>
    #                                   </table></p>""")
    

    # def sendDetails(self, request, recipient, url):
    #     search = re.search('/#details/([a-z0-9]+)/', url)
    #     if search is None:
    #         return
    #     else:
    #         doc_id = search.group(1)
    #         d = couch.openDoc(doc_id)
    #         return d

    
    # def sendFavorites2(self, res, request, recipient):
    #     rows = []
    #     for _row in res['rows']:
    #         row = _row['value']
    #         rows.append(self.favorites_template.substitute({'subj':row['subj'],'body':row['text'],
    #                                                    'phone':row['phone'], 'price':row['price']}))
    #     url = Template('<p><a href="$url">$url</a></p>')
    #     user_id = request.getCookie('kalog_user')        
    #     d = send_email(recipient, u'Избранное',  url.substitute({'url':'http://kalog.ru/#favorites/' + user_id + '/'})
    #                    + u''.join(rows))
    #     d.addCallback(self.end, request)
                      


    # def sendFavorites1(self, user_doc, request, recipient):
    #     d = couch.openView(designID, 'short_docs_by_id',
    #                        keys=user_doc['favorites'])
        
    #     d.addCallback(self.sendFavorites2, request, recipient)
    #     return d

    # def sendFavorites(self, request, recipient):
    #     user_id = request.getCookie('kalog_user')
    #     d = couch.openDoc(user_id)
    #     return d



    def render_GET(self, request):
	recipient = unicode(unquote_plus(request.args.get('email', [''])[0]), 'utf-8')
	uuid = unicode(unquote_plus(request.args.get('uuid', [''])[0]),'utf-8')

	if len(uuid) == 0 or len(recipient) == 0:
	    return "-1"
        send_email(recipient, u'Купить компьютер просто',  'http://buildpc.ru/computer/'+uuid)
	return "ok"

def send_email(recipient, subject, body, sender=u'Компьютерный магазин <inbox@buildpc.ru>'):
    """Send an email.

    All arguments should be Unicode strings (plain ASCII works as well).

    Only the real name part of sender and recipient addresses may contain
    non-ASCII characters.

    The email will be properly MIME encoded and delivered though SMTP to
    localhost port 25.  This is easy to change if you want something different.

    The charset of the email will be the first one out of US-ASCII, ISO-8859-1
    and UTF-8 that can represent all the characters occurring in the email.
    """

    # Header class is smart enough to try US-ASCII, then the charset we
    # provide, then fall back to UTF-8.
    header_charset = 'ISO-8859-1'

    # We must choose the body charset manually
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
	try:
	    body.encode(body_charset)
	except UnicodeError:
	    pass
	else:
	    break

    # Split real name (which is optional) and email address parts
    sender_name, sender_addr = parseaddr(sender)
    recipient_name, recipient_addr = parseaddr(recipient)

    # We must always pass Unicode strings to Header, otherwise it will
    # use RFC 2047 encoding even on plain ASCII strings.
    sender_name = str(Header(unicode(sender_name), header_charset))
    recipient_name = str(Header(unicode(recipient_name), header_charset))

    # Make sure email addresses do not contain non-ASCII characters
    sender_addr = sender_addr.encode('ascii')
    recipient_addr = recipient_addr.encode('ascii')

    # Create the message ('plain' stands for Content-Type: text/plain)
    #msg = MIMEText(body.encode(body_charset), 'plain', body_charset)
    msg = MIMEMultipart('alternative')
    part = MIMEText(body.encode(body_charset), 'html', body_charset)
    msg.attach(part)

    msg['From'] = formataddr((sender_name, sender_addr))
    msg['To'] = formataddr((recipient_name, recipient_addr))
    msg['Subject'] = Header(unicode(subject), body_charset)

    msg = StringIO(str(msg))
    d = defer.Deferred()
    factory = ESMTPSenderFactory(sender_addr, mailpassword, sender_addr, recipient, msg, d, requireTransportSecurity=False)
    reactor.connectTCP('smtp.yandex.ru', 587, factory)
    return d
