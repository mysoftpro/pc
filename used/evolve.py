from pc.used.couch import couch, designID
from twisted.internet import reactor, defer

def fixDubbies(res):
    keys = set()
    dubbies = {}
    for r in res['rows']:
        if r['key'] in keys:
            dubbies.update({r['id']:r['value']})
        else:
            keys.add(r['key'])
    print "dubbies: "+str(len(dubbies))
    mock = defer.Deferred()
    def _del(k,v):
        def __del(some):
            couch.deleteDoc(k,v)
        return __del
    for k,v in dubbies.items():
        mock.addCallback(_del(k,v))
    return mock.callback(None)
                               

def evolve():
    d = couch.openView(designID, "external_ids", stale=False)
    d.addCallback(fixDubbies)
    return d
