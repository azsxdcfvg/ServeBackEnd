# state 0:关机 1:开机且送风 2:开机不送风
# mode -1:制冷 1:制热
# wind 1 - 3
#
import threading
import datetime
import time
import math

totaltime = 0.5


class Slave:
    def __init__(self, initemp: float, curtemp: float, aimtemp: float, mode: int, wind: int, state: int, ratio: float, roomid: int, price: float = 0):
        self.initemp = initemp
        self.curtemp = curtemp
        self.aimtemp = aimtemp
        self.mode = mode
        self.wind = wind
        self.state = state
        self.ratio = ratio
        self.price = price
        self.roomid = roomid
        self.starttime = datetime.datetime.now()
        self.isdispatched = 0

    def tempchange(self):
        if self.state == 0 or self.state == 2:
            # self.curtemp += self.initemp - self.curtemp
            if math.fabs(self.curtemp - self.initemp) >= (0.5 * totaltime):
                print(114514)
                if self.initemp > self.curtemp:
                    self.curtemp += 0.5 * totaltime
                else:
                    self.curtemp -= 0.5 * totaltime
        if self.state == 1:
            if self.wind == 3:
                bias = 0.6
            elif self.wind == 2:
                bias = 0.5
            else:
                bias = 0.4
            if math.fabs(self.curtemp - self.aimtemp) < bias * totaltime:
                self.curtemp = self.aimtemp
                self.state = 2
            if self.mode == -1 and self.curtemp > self.aimtemp and math.fabs(self.curtemp - self.aimtemp) >= bias * totaltime:
                self.curtemp = self.curtemp - (0.5 + (self.wind - 1) * 0.1) * totaltime
                self.price += 1 / (4 - self.wind) * totaltime
            if self.mode == 1 and self.curtemp < self.aimtemp:
                self.curtemp = self.curtemp + (0.5 + (self.wind - 1) * 0.1) * totaltime
                self.price += (1 / (4 - self.wind)) * totaltime

    def __str__(self):
        return str(self.initemp) + " " + str(self.curtemp) + " " + str(self.aimtemp) + " " + str(self.mode) + " " \
               + str(self.wind) + " " + str(self.state) + " " + str(self.ratio) + " " + str(self.price)

    def setstate(self, state: int):
        self.state = state

    def getdata(self) -> list:
        return [self.initemp, self.curtemp, self.aimtemp, self.mode, self.wind, self.state, self.ratio, self.price, self.roomid]

    def wrap(self):
        return {"initemp": self.initemp, "curtemp": self.curtemp, "aimtemp": self.aimtemp, "mode": "制热" if self.mode == 1 else "制冷",
                "wind": ["高", "中", "低"][self.wind], "state": ["关机", "开机且送风", "开机不送风"][self.state], "ratio": self.ratio, "price": self.price, "roomid": self.roomid}


class myThread2(threading.Thread):
    def __init__(self, slavelist: list):
        threading.Thread.__init__(self)
        self.slavelist = slavelist

    def run(self):
        while True:
            self.changetem(self.slavelist)
            time.sleep(totaltime)

    def changetem(self, slavelist: list):
        for slave in slavelist:
            slave.tempchange()
