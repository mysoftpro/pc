# -*- coding: utf-8 -*-
from datetime import datetime

def addCookies(request, cookies):
    now = datetime.now()
    localhost = request.getRequestHostname()=='localhost'
    if localhost:
	request.addCookie('pc_cookie_forced1','true',expires=now.replace(year=2038).strftime('%a, %d %b %Y %H:%M:%S UTC'),path='/')
    for k,v in cookies.items():
	year = 2038
	if v=='':
	    year = 2000
	t = now.replace(year=year).strftime('%a, %d %b %Y %H:%M:%S UTC')
	if not localhost:
	    request.addCookie(str(k),str(v),expires=t,path='/',domain='.buildpc.ru')
	else:
	    request.addCookie(str(k),str(v),expires=t,path='/')


class forceCond(object):
    def __init__(self, beforeCond, deferedCreator):
        self.beforeCond = beforeCond
        self.deferedCreator = deferedCreator

    def __call__(self, afterProc):
        def chainning(*args, **kwargs):
            retval = None
            if self.beforeCond():
                retval = afterProc(*args, **kwargs)
            else:
                retval = self.deferedCreator()
                retval.addCallback(lambda some: afterProc(*args, **kwargs))
            return retval
        return chainning

def MIMETypeJSON(f):
    def render(self, request):
        request.setHeader('Content-Type', 'application/json;charset=utf-8')
	request.setHeader("Cache-Control", "max-age=0,no-cache,no-store")
        return f(self, request)
    return render


def pcCartTotal(request, user):
    in_cart = 0
    if 'models' in user:
        in_cart += len(user['models'])
    if 'notebooks' in user:
        in_cart+=len(user['notebooks'].keys())
    #TODO! may be 1 set is just 1 set,  not video+power?
    if 'sets' in user:
        in_cart += len(user['sets'])
    # if 'sets' in user:
    #     for s in user['sets']:             
    #         for v in s.values():
    #             pcs = 1
    #             if 'pcs' in v:
    #                 pcs = v['pcs']
    #         in_cart+=pcs
    if in_cart>0:
        addCookies(request, {'pc_cart':str(in_cart)})
