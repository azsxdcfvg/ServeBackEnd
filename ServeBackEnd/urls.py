from django.urls import path
from django.http import HttpResponse
from .core import Aircon

import json
from .core.Aircon import Request

AirCondition = Aircon.Aircon()
DataBase = AirCondition.handle.logindbhandler
'''
room_id = 0
kind = -1  # 0表示开机请求 1表示送风请求 2表示关机请求
temp = 25  # 默认25度  ！！！设定如果只改了风速，则温度设定为-1
speed = 1  # 默认中风，用int来表示风速，方便比较  ！！！同样，如果只改变了温度，则风速设为-1
'''


def getStatus(req):
    print(req.GET)
    idx = req.GET.idx
    ret = AirCondition.getConditon(idx)
    print(ret)
    return HttpResponse(json.dumps({"code": 0, "msg": ret}))


def switchMode(req):
    print(req.GET)
    reqs = Request(room_id=req.GET.room_id, kind=req.GET.kind, temp=req.GET.temp, speed=req.GET.speed)
    ret = AirCondition.echoRequest(reqs)
    return HttpResponse(json.dumps({"code": 0, "msg": ret}))


def login(req):
    print(req.GET)
    res = DataBase.isExist(req.GET.get("name"), req.GET.get("pass"), req.GET.get("mode"))
    return HttpResponse(json.dumps({"code": 0, "msg": str(res)}))


def ping(req):
    print(req.GET)
    AirCondition.ping()
    return HttpResponse("pong")


urlpatterns = [
    path('getStatus', getStatus),
    path('switchMode', switchMode),
    path('ping', ping),
    path('login', login),
]
