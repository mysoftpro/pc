# -*- coding: utf-8 -*-
from twisted.internet import protocol
from cStringIO import StringIO
import sys
import simplejson
from datetime import date

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
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Image, Spacer
# we know some glyphs are missing, suppress warnings
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from pc import root
from reportlab.lib import colors

def main():

    json = simplejson.loads(unicode(sys.stdin.read(), 'utf-8'))


    _today = date.today()
    today = '.'.join([str(_today.day),str(_today.month),str(_today.year)])
    bill_text = (u'Счет на оплату заказа 234567-'+json['_rev'].split('-')[0]+\
                     u' от '+today).encode('utf-8')

    pdfmetrics.registerFont(TTFont('Ubuntu', 'Ubuntu-R.ttf'))
    pdfmetrics.registerFont(TTFont('UbuntuBd', 'Ubuntu-B.ttf'))
    pdfmetrics.registerFont(TTFont('UbuntuIt', 'Ubuntu-I.ttf'))
    pdfmetrics.registerFont(TTFont('UbuntuBI', 'Ubuntu-BI.ttf'))


    styles = getSampleStyleSheet()
    styles['Normal'].fontName='Ubuntu'
    styles['Heading3'].fontName='UbuntuBd'
    styleN = styles['Normal']
    styleH = styles['Heading3']

    story = []

    path = os.path.join('/'.join(root.__file__.split('/')[:-1]), 'pdf_logo.png')
    im = Image(path)
    im.hAlign = 'LEFT'
    story.append(im)
    title = Paragraph(u'<font size="10">Компьютерный магазин Билд</font>'.encode('utf-8'), styleN)
    link = Paragraph(u'<font size="10"><a href="http://buildpc.ru/cart/'\
                         +json['author']+'">http://buildpc.ru/cart/'+json['author']+'</a></font>'.encode('utf-8'), styleN)
    story.append(title)
    story.append(link)
    story.append(Spacer(50,50))


    tableStyle = TableStyle([('FONTNAME', (0,0), (-1,-1), 'Ubuntu'),
                             ('FONTSIZE', (0,0), (-1,-1), 10),
                             ('GRID', (0,0), (1,0), 1,colors.black),
                             ('SPAN',(2,0),(2,2)),
                             ('SPAN',(3,0),(3,2)),

                             
                             ('SPAN',(2,4),(2,5)),
                             ('SPAN',(3,4),(3,5)),
                             ('GRID', (2,0), (2,5), 1,colors.black),
                             #('GRID', (3,0), (3,5), 1,colors.black),
                             ('BOX',(3,0),(3,3),1,colors.black),
                             ('BOX',(3,4),(3,5),1,colors.black),

                             ('BOX',(0,1),(1,2),1,colors.black),
                             ('BOX',(0,3),(1,5),1,colors.black),
                             ])


    bill_data = [[u'ИНН 390606738176',u'КПП _',u'Сч.No',u'40802810620970000084'],
                 [u'Получатель',u'',u'',u''],
                 [u' Индивидуальный предприниматель Ганжа Алексей Юрьевич',u'',u'',u''],
                 [u'Банк получателя',u'',u'БИК',u'042748634'],
                 [u'ОТДЕЛЕНИЕ N8626 СБЕРБАНКА РОССИИ г.',u'',u'Сч.No',u'30101810100000000634'],
                 [u'КАЛИНИНГРАД МОСКОВСКИЙ ПР.,24',u'',u'',u'']]
    bill_data_encoded = []
    for row in bill_data:
        e_row = []        
        for cell in row:
            e_row.append(cell.encode('utf-8'))
        bill_data_encoded.append(e_row)            
        
    story.append(Table(bill_data_encoded, style=tableStyle))


    p1 = Paragraph('<para spaceBefore="50" leftIndent="120">'+bill_text+'</para>',
                   styleH)
    story.append(p1)


    data = []
    col = 1
    summ = 0
    for cat,code in json['items'].items():
        pcs = 1
        if type(code) is list:
            pcs = len(code)
            code = code[0]
        item = [i for i in json['full_items'] if i['_id']==code][0]
        data.append([str(col),
                     item['text'].encode('utf-8'),
                     pcs,
                     str(item['price']),
                     str(item['price']*pcs),
                     ])
        summ += item['price']*pcs
        col+=1

    # TODO! proper dvd
    if 'dvd' in json and json['dvd']:
        data.append([str(col),
                     u'Дисковод Samsung SH-222AB/BEBE 22x SATA BLACK'.encode('utf-8'),
                     '1',
                     str(json['const_prices'][0]),
                     str(json['const_prices'][0]),
                     ])
        summ += json['const_prices'][0]
        col+=1
    if 'building' in json and json['building']:
        data.append([str(col),
                     u'Услуги сборки'.encode('utf-8'),
                     '1',
                     str(json['const_prices'][1]),
                     str(json['const_prices'][1]),
                     ])
        summ += json['const_prices'][1]
        col+=1
    if 'installing' in json and json['installing']:
        data.append([str(col),
                     u'Услуги установки программного обеспечения'.encode('utf-8'),
                     '1',
                     str(json['const_prices'][2]),
                     str(json['const_prices'][2]),
                     ])
        summ += json['const_prices'][2]
        col+=1
    data.insert(0,['#',
                 u'Наименование'.encode('utf-8'),
                 u'Кол-во'.encode('utf-8'),
                 u'Цена р.'.encode('utf-8'),
                 u'Сумма р.'.encode('utf-8')])
    story.append(Table(data, style=TableStyle([('FONTNAME', (0,0), (-1,-1), 'Ubuntu'),
                             ('FONTSIZE', (0,0), (-1,-1), 6),
                             ('GRID', (0,0), (-1,-1), 1,colors.black),])))
    tot = Paragraph((u'<para spaceBefore="10" leftIndent="350">Итого: '+str(summ)+\
                     u' рублей').encode('utf-8'),styleN)
    story.append(tot)
    nds = Paragraph((u'<para leftIndent="350">НДС не предусмотрен</para>').encode('utf-8'),styleN)
    story.append(nds)

    doc = SimpleDocTemplate(sys.stdout,pagesize=A4,leftMargin=20,topMargin=20,
                            author=u'Компьютерный магазин Билд'.encode('utf-8'),
                            title=bill_text)
    doc.build(story)
    sys.exit(0)

if __name__ == "__main__":
    main()
