from django.urls import path
from django.http import Http404, HttpResponse

import json


def getTemp(req):
    mp = json.loads(req.body)
    print(mp)
    return HttpResponse(json.dumps({"code": 0, "msg": 1}))


def getCost(req):
    mp = json.loads(req.body)
    print(mp)
    return HttpResponse(json.dumps({"code": 0, "msg": 2}))


def switchMode(req):
    mp = json.loads(req.body)
    print(mp)
    return HttpResponse(json.dumps({"code": 0, "msg": True}))


def switchOn(req):
    mp = json.loads(req.body)
    print(mp)
    return HttpResponse(json.dumps({"code": 0, "msg": True}))


def switchTemp(req):
    mp = json.loads(req.body)
    print(mp)
    return HttpResponse(json.dumps({"code": 0, "msg": True}))


urlpatterns = [
    path('getTemp', getTemp),
    path('getCost', getCost),
    path('switchMode', switchMode),
    path('switchOn', switchOn),
    path('switchTemp', switchTemp),
]
