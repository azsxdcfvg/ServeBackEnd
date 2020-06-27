from django.urls import path
from django.http import HttpResponse
from django.utils.decorators import method_decorator

from .core import Aircon
from django.views.decorators.csrf import csrf_exempt

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


@method_decorator(csrf_exempt)
def getPay(req):
    mp = json.loads(req.body)
    idx = mp.get("idx")
    return HttpResponse("pong")


@method_decorator(csrf_exempt)
def getAnalyze(req):
    mp = json.loads(req.body)
    idx = mp.get("idx")
    return HttpResponse("pong")


@method_decorator(csrf_exempt)
def getStatus(req):
    mp = json.loads(req.body)
    idx = mp.get("idx")
    ret = AirCondition.getConditon(idx)
    return HttpResponse(json.dumps({"code": 0, "msg": ret}))


def getAll(req):
    ret = []
    for i in range(AirCondition.room_amount):
        ret.append(AirCondition.airs[i].wrap())
    return HttpResponse(json.dumps({"code": 0, "msg": ret}))


@method_decorator(csrf_exempt)
def switchMode(req):
    print(req.body)
    mp = json.loads(req.body)
    reqs = Request(room_id=mp.get("room_id"), kind=mp.get("kind"), temp=mp.get("temp"), speed=mp.get("speed"))
    ret = AirCondition.echoRequest(reqs)
    return HttpResponse(json.dumps({"code": 0, "msg": ret}))


@method_decorator(csrf_exempt)
def login(req):
    print(req.body)
    mp = json.loads(req.body)
    print(mp)
    res = DataBase.isExist(mp.get("name"), mp.get("pass"), mp.get("mode"))
    return HttpResponse(json.dumps({"code": 0, "msg": str(res)}))


def ping(req):
    mp = json.loads(req.body)
    print(mp)
    AirCondition.ping()
    return HttpResponse("pong")


urlpatterns = [
    path('getStatus', getStatus),
    path('switchMode', switchMode),
    path('ping', ping),
    path('login', login),
    path('getAll', getAll),
    path('getPay', getPay),
    path('getAnalyze', getAnalyze),
]
