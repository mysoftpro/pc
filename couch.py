from paisley import CouchDB
from pc.secure import couchadmin, couchpassword

import os
import os.path

def pr(failure):
    print failure

def getDesign(failure):
    d = None
    if str(failure.value).startswith('404'):
        d = couch.saveDoc('{}', design_id)
        d.addCallback(syncViews)
        d.addErrback(pr)
        return d


couch = CouchDB('localhost', dbName='pc', username=couchadmin, password=couchpassword)
design_id = "_design/pc"
designID = "pc"


this_file = __file__

def syncViews(designDoc):
    if 'views' not in designDoc:
        designDoc['views'] = {}
    jsondir = os.path.join(os.path.dirname(this_file), 'json')
    files = [f for f in os.listdir(jsondir) if f.endswith('.js')]
    new_design = {'views':{}}
    new_design['_id'] = design_id
    new_design['_rev'] = designDoc['_rev']
    map_files = [f for f in  files if 'map' in f.split('.')]

    for f in map_files:
        view_name = f.split('/')[-1].split('.')[0]
        map_file = open(os.path.join(os.path.dirname(this_file), 'json', f))
        _map = map_file.read()
        map_file.close()
        _reduce = None
        reduce_file_name = f.replace("map","reduce")
        if os.path.isfile(os.path.join(os.path.dirname(this_file), 'json', reduce_file_name)):
            reduce_file = open(os.path.join(os.path.dirname(this_file), 'json', reduce_file_name))
            _reduce = reduce_file.read()
            reduce_file.close()
        view = {}
        view['map'] = _map
        if _reduce is not None:
            view['reduce'] = _reduce
        new_design['views'][view_name] = view

    def compDicts(di1, di2):
        changed = False
        def getcha(element):
            print "getcha!"
            print element
            return True
        try:
            for el in di1:
                # something was deleted
                if el not in di2:
                    changed = getcha(el)
                    break
                for eel in di1[el]:                    
                    if eel not in di2[el]:
                        changed = getcha(eel)
                        break
                    if di1[el][eel] != di2[el][eel]:
                        # print "fuck!"
                        # print type(di1[el][eel])
                        # print type(di2[el][eel])
                        # print di1[el][eel].encode('utf-8')
                        # print di2[el][eel].encode('utf-8')
                        changed = getcha((di1[el][eel],di2[el][eel]))
                        break
        except Exception, e:
            print "fuuuuuuuuuuuuuuuuuuuuuuuuuck"
            print e
        return changed
    res = None
    if compDicts(designDoc['views'], new_design['views']) or compDicts(new_design['views'], designDoc['views']):
        print "stooooooooooooooooooooooooore new design"
        res = couch.saveDoc(new_design)
        def pr(res):
            print res
        res.addCallback(pr)
        res.addErrback(pr)
    print "finish syncing"
    return res

    # for el in new_design:
    #     # something added
    #     if el not in designDoc:
    #         changed = True
    #         for eel in el:
    #             if eel not in designDoc[el]:
    #                 changed = True
    #                 break
    #             if new_design[el][eel] != designDoc[el][eel]:
    #                 changed = True
    #                 break



d = couch.openDoc(design_id)
d.addCallback(syncViews)
d.addErrback(pr)
