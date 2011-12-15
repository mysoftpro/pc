# -*- coding: utf-8 -*-
from twisted.internet import protocol
from cStringIO import StringIO
import sys
import simplejson

class PdfWriter(protocol.ProcessProtocol):
    def __init__(self, data, d):
        self.data = data
        self.encoded = StringIO()
        self.d = d

    def connectionMade(self):
        self.transport.write(self.data)
        self.transport.closeStdin()


    def outReceived(self, data):
        self.encoded.write(data)

    def outConnectionLost(self):
        self.transport.loseConnection()
        self.d.callback(self.encoded.getvalue())

    def processEnded(self, reason):
        pass

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate
# we know some glyphs are missing, suppress warnings
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def main():
    pdfmetrics.registerFont(TTFont('Ubuntu', 'Ubuntu-R.ttf'))
    pdfmetrics.registerFont(TTFont('UbuntuBd', 'Ubuntu-B.ttf'))
    pdfmetrics.registerFont(TTFont('UbuntuIt', 'Ubuntu-I.ttf'))
    pdfmetrics.registerFont(TTFont('UbuntuBI', 'Ubuntu-BI.ttf'))


    styles = getSampleStyleSheet()
    styles['Normal'].fontName='Ubuntu'
    styles['Heading1'].fontName='UbuntuBd'
    styleN = styles['Normal']
    styleH = styles['Heading1']
    story = []
    # add some flowables
    cyr = u"This is a paragraph in <i>ХаХав</i> style.".encode('utf-8')
    p1 = Paragraph("This is a Heading",styleH)
    p2 = Paragraph(cyr,styleN)

    story.append(p1)
    story.append(p2)

    json = simplejson.loads(unicode(sys.stdin.read(), 'utf-8'))
    for doc in json['full_items']:
        story.append(Paragraph(doc['text'].encode('utf-8'), styleN))


    doc = SimpleDocTemplate(sys.stdout,pagesize=A4,
                            author=u'Компьютерный магазин Билд'.encode('utf-8'),
                            title=u'Счет на оплату заказа 234567 от 23.12.2011'.encode('utf-8'),)
    doc.build(story)

    # sys.stdout.write('Hellow!')
    sys.exit(0)

if __name__ == "__main__":
    main()
