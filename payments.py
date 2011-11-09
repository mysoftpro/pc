# -*- coding: utf-8 -*-
from twisted.web.resource import Resource
from pc.secure import do_key
import hashlib
from lxml import etree
from copy import deepcopy

class DOValidateUser(Resource):
    def __init__(self):
        self.xml = etree.XML('<result></result>')
        code = etree.Element('code')
        self.xml.append(code)
        
    def render_POST(self, request):
        userid = request.args.get('userid',[None])[0]
        # userid_extra = request.args.get('userid_extra',[None])[0]
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
            answer.find('code').text = 'Yes'
        else:
            answer.find('code').text = 'No'
            
        return etree.tostring(answer, encoding='utf-8', xml_declaration=True)
