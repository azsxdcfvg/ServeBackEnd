from .Queue import *
from .Airs import *
from .Database import *


class Request:
    room_id = 0
    kind = -1  # 0表示开机请求 1表示送风请求 2表示关机请求
    temp = 25  # 默认25度  ！！！设定如果只改了风速，则温度设定为-1
    speed = 2  # 默认中风，用int来表示风速，方便比较  ！！！同样，如果只改变了温度，则风速设为-1

    def __init__(self, kind, temp, speed, room_id):
        print(kind, temp, speed, room_id)
        self.kind = int(kind)
        self.temp = int(temp)
        self.speed = int(speed)
        self.room_id = int(room_id)

    def __str__(self):
        return str(self.kind) + " " + str(self.temp) + " " + str(self.speed) + " " + str(self.room_id)


class Aircon:
    room_amount = 0
    available_amount = 0

    def __init__(self):
        self.room_amount = 5  # 房间总数
        self.available_amount = 3  # 最多能服务的房间数
        start = time.process_time()
        self.start = start

        self.queue = Queue(start)  # 初始化队列
        self.airs = []  # 初始化空调列表
        for i in range(self.room_amount):
            temp = Slave(28, 28, 25, -1, 2, 0, 0.5, 301 + i)
            self.airs.append(temp)

        # 开启线程1,负责检测等待队列
        print("开启线程1: 检测等待队列是否有请求可以被调度")
        self.thread1 = myThread1(self.queue)
        self.thread1.start()

        # 开启线程二,负责模拟房间温度变化
        print("开启线程2: 模拟房间温度变化")
        self.thread2 = myThread2(self.airs)
        self.thread2.start()
        self.handle = dbHandler("example2.db")
        self.datahandle = self.handle.datadbhandler

    # 响应请求
    def echoRequest(self, request):
        print(str(request))
        if request.kind == 0:  # 开机请求
            print("开机")
            if request.room_id not in self.queue.running_list2:  # 如果此时空调没有处在开机状态
                if len(self.queue.running_list) < self.available_amount:  # 如果此时服务对象没有满员
                    end = time.process_time()
                    t1 = end - self.start
                    self.queue.running_list.append([request.room_id, t1, request.speed, request.temp])
                    self.queue.running_list2.append(request.room_id)

                    # 另加
                    self.airs[len(self.queue.running_list) - 1].starttime = datetime.datetime.now()
                    self.changeairs(request, 1)

                    # 2开机时不需要写数据库

                    return 0  # 表示成功响应请求
                else:
                    for i in range(len(self.queue.running_list)):  # 查看该请求是否可以调换出running_list里的请求
                        if self.queue.running_list[i][2] < request.speed:
                            # 移除优先级较低的请求到等待队列
                            temp_list = self.queue.running_list.pop(i)
                            end = time.process_time()
                            t2 = end - self.start
                            temp_list[1] = t2
                            self.queue.waiting_list.append(temp_list)
                            self.queue.waiting_list2.append(self.queue.running_list[i][0])
                            self.queue.running_list2.remove(self.queue.running_list[i][0])

                            # 2移除时由于状态改变,需要将该段移除的数据写数据库
                            # running_list 列表里放的是列表类型，各元素对应着 房间号 请求开始响应的时间点 风速 温度
                            # writeData(self, roomId: int, startTime: str, endTime: str, windSpeed: int
                            # , price: float, mode: int, ratio: float, aimteproture: int, isdispatch: int):

                            p = request.room_id - 301  # 用于获取相应从机数据的下标
                            self.datahandle.writeData(self.airs[p].roomid, self.airs[p].starttime, datetime.datetime.now()
                                                      , self.airs[p].wind, self.airs[p].price, self.airs[p].mode
                                                      , self.airs[p].ratio, self.airs[p].aimtemp, self.airs[p].isdispatched)

                            # 把新请求加入到running_list
                            end = time.process_time()
                            t3 = end - self.start
                            self.queue.running_list.append([request.room_id, t3, request.speed, request.temp])
                            self.queue.running_list2.append(request.room_id)
                            self.changeairs(request, 1)

                            # !!!还要加上对数据库的操作 修改房间信息
                            # 一个请求完成的时候才需要写数据库
                            return 0  # 表示成功响应请求

                    # 如果前面函数没有返回，说明该请求比不上running_list里任何请求的优先级，直接进入waiting_list
                    end = time.process_time()
                    t4 = end - self.start
                    self.queue.waiting_list.append([request.room_id, t4, request.speed, request.temp])
                    self.queue.waiting_list2.append(request.room_id)
                    self.changeairs(request, 0)
                    return 1  # 表示该请求正在等待中，两分钟之后开始实施
            else:
                return -2  # 已经开机的空调不再响应开机请求

        elif request.kind == 1:  # 调风请求
            print("修改送风")
            if request.room_id not in self.queue.running_list2:  # 如果空调根本还没开机
                return -2  # 还没开机的空调不能接收调风请求
            elif request.room_id in self.queue.waiting_list2:  # 如果空调还处在等待队列里,修改最新请求
                for i in range(len(self.queue.waiting_list)):
                    if request.room_id == self.queue.waiting_list[i][0]:
                        if request.speed != -1:
                            self.queue.waiting_list[i][2] = request.speed
                        if request.temp != -1:
                            self.queue.waiting_list[i][3] = request.temp
                        # !!!不用加数据库的操作，没被正式调度都不用改
                        self.changeairs(request, 0)
                        return 1  # 表示该请求正在等待中，据第一次提出请求两分钟后开始实施
            else:  # 空调已经在运行队列里
                for i in range(len(self.queue.running_list)):
                    if request.room_id == self.queue.running_list[i][0]:
                        if request.speed != -1:
                            self.queue.running_list[i][2] = request.speed
                        if request.temp != -1:
                            self.queue.running_list[i][3] = request.temp

                        p = request.room_id - 301
                        self.datahandle.writeData(self.airs[p].roomid, self.airs[p].starttime, datetime.datetime.now()
                                                  , self.airs[p].wind, self.airs[p].price, self.airs[p].mode
                                                  , self.airs[p].ratio, self.airs[p].aimtemp, self.airs[p].isdispatched)

                        self.changeairs(request, 1)
                        return 0  # 表示成功响应请求

        elif request.kind == 2:  # 关机请求
            print("关")
            if request.room_id not in self.queue.running_list2:
                return -2  # 表示响应无效，此时空调根本没开机
            else:
                self.queue.running_list2.remove(request.room_id)
                index = -1
                for i in range(len(self.queue.running_list)):
                    if self.queue.running_list[i][0] == request.room_id:
                        index = i
                        break
                del self.queue.running_list[index]

                # !!!还要加上对数据库的操作 修改房间信息
                p = request.room_id - 301
                self.datahandle.writeData(self.airs[p].roomid, self.airs[p].starttime, datetime.datetime.now()
                                          , self.airs[p].wind, self.airs[p].price, self.airs[p].mode
                                          , self.airs[p].ratio, self.airs[p].aimtemp, self.airs[p].isdispatched)

                self.changeairs(request, 0)

                return 0  # 表示成功响应请求

        else:
            return -1  # 返回-2表示请求出错，因为请求的类型都不对

    # 该函数用于根据不同请求和返回结果,修改空调的状态
    def changeairs(self, request, waitorrun):
        for i in range(len(self.airs)):
            if request.room_id == self.airs[i].roomid:
                self.airs[i].starttime = datetime.datetime.now()
                if request.kind == 0:  # 开机请求,修改state
                    self.airs[i].state = waitorrun  # 这个参数表示是等待送风还是开始送风
                    break

                elif request.kind == 1:  # 调风请求
                    if request.speed != -1:
                        self.airs[i].wind = request.speed
                        self.airs[i].isdispatched = 1
                        self.airs[i].ratio = 1 / self.airs[i].wind
                    else:
                        self.airs[i].isdispatched = 0
                    if request.temp != -1:
                        self.airs[i].aimtemp = request.temp
                    self.airs[i].state = waitorrun
                    break

                elif request.kind == 2:  # 关机请求
                    self.airs[i].state = 0
                    break

                else:
                    print("请求类型出错")

    # 该函数用于检测空调的状态
    def listenrunning(self):
        for air in self.airs:
            if air.state == 1 and air.aimtemp == air.curtemp:
                request = Request(1, air.aimtemp, air.wind - 1, air.roomid)
                self.echoRequest(request)

            elif air.state == 2 and air.curtemp - air.aimtemp > 1:
                request = Request(1, air.aimtemp, air.wind - 1, air.roomid)
                self.echoRequest(request)

    def ping(self):
        print("pong")

    def getConditon(self, idx):
        if len(self.airs) - 1 < idx:
            return []
        else:
            return self.airs[idx].wrap()

    def getPay(self, idx, when):
        ret = self.handle.datadbhandler.getDataForDetail(idx, '"' + when + '"')
        return ret

    def getAnalyze(self, mode):
        ret = self.handle.datadbhandler.getDataForTable(mode)
        return ret


class myThread3(threading.Thread):
    def __init__(self, aircon):
        threading.Thread.__init__(self)
        self.aircon = aircon

    def run(self):
        while True:
            self.aircon.listenrunning()
            time.sleep(0.5)

# 总结一下调度算法
# 开机时，判断服务对象是否满员，没有满直接响应，满了的话加入等待行列
# 提出请求时，无论该房间处于开机还是等待响应，都修改新请求方案
# 有一个疑问是：这样不完整的调度方案可能造成明明服务对象没有满员，但等待队列里仍有请求
# 比如说，有一个房间开了空调之后队伍满员，但他不到10s就关了，按照规定，等待队列里的请求必须等两分钟
# 等待解决
