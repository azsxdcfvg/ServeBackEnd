import sqlite3 as sq
import datetime
import time
import base64
from hashlib import md5

dataBaseName = "example2.db"
loginTableName = "userinfo"
dataTableName = "airinfo2"
limitTime = 20
roomnum = 5


class dbHandler:
    def __init__(self, dbname):
        self.dbname = dbname
        self.con = sq.connect(dbname, limitTime, check_same_thread=False)
        self.cursor = self.con.cursor()
        try:
            self.cursor.execute("create table airinfo2(\
                                    roomid int not null, \
                                    starttime date not null,\
                                    endtime date not null,\
                                    windspeed int not null,\
                                    price real not null,\
                                    mode int ,\
                                    ratio real not null,\
                                    aimtemproture int not null,\
                                    isdispatch int not null,\
                                    primary key (roomid, starttime));")
            self.cursor.execute("create table userinfo(\
                                    username varchar(20) primary key not null,\
                                    password varchar(20) not null,\
                                    mode int not null);")
        except Exception as e:
            pass
        self.con.commit()
        self.datadbhandler = datadbHandler(self.cursor, self.con)
        self.logindbhandler = logindbHandler(self.cursor, self.con)
        # self.sessionid = ""


class datadbHandler:
    def __init__(self, cursor, con):
        self.tbname = dataTableName
        self.cursor = cursor
        self.con = con

    # 向数据库写数据
    def writeData(self, roomId: int, startTime: str, endTime: str, windSpeed: int
                  , price: float, mode: int, ratio: float, aimteproture: int, isdispatch: int):
        print("insert into " + self.tbname + " values" + "(" + str(roomId) + ',' + str(startTime) + ',' + str(endTime) + ','
              + str(windSpeed) + ',' + str(price) + ',' + str(mode) + ',' + str(ratio) + ')')
        try:
            self.cursor.execute('insert into ' + self.tbname + ' values' + '(' + str(
                roomId) + ',"' + str(startTime) + '","' + str(endTime) + '",' + str(windSpeed) + ',' + str(price) + ','
                                + str(mode) + ',' + str(ratio) + ',' + str(aimteproture) + ',' + str(isdispatch) + ')')
            self.con.commit()
        except Exception as e:
            print("data写数据失败", e)
            raise Exception

    # 获得详单数据
    def getDataForDetail(self, roomId: int, startTime: str):
        print("select * from " + self.tbname + ' where startTime > ' + str(startTime) + ' and ' + "roomid = " + str(roomId))
        try:
            self.cursor.execute("select * from " + self.tbname + ' where startTime >= ' + str(startTime) + ' and ' + "roomid = " + str(roomId))
            # self.cursor.execute("select * from " + self.tbname)
            query_result = self.cursor.fetchall()
            print(query_result)
            self.con.commit()
            return query_result
        except Exception as e:
            print("详单数据获取出错", e)
            raise Exception

    # 按需求返回报表数据,默认返回日报表d日,m月,y年
    def getDataForTable(self, mode: str = 'd') -> dict:
        # 按照参数提取年/月/日报表

        currenttime = datetime.datetime.now()
        # 不需要后面的具体时间
        currenttime = str(currenttime.strftime("%Y-%m-%d %H:%M:%S")).split(" ")[0]

        if mode == 'd':
            currenttime = currenttime + " 00:00:00"
        elif mode == 'm':
            currenttime = currenttime[0:8] + "01 00:00:00"
        elif mode == 'y':
            currenttime = currenttime[0:5] + "01-01 00:00:00"
        print("select * from " + self.tbname + " where startTime > " + '"' + str(currenttime) + '"')
        self.cursor.execute("select * from " + self.tbname + " where startTime > " + '"' + str(currenttime) + '"')
        query_result = self.cursor.fetchall()
        self.con.commit()

        # 查询结果
        print(query_result)
        return self.gettabledata(query_result)

    def gettabledata(self, query_result: list):
        sort = {}
        for i in range(len(query_result)):
            try:
                sort[query_result[i][0]].append(query_result[i])
            except KeyError:
                sort[query_result[i][0]] = [query_result[i]]

        keys = list(sort.keys())

        result = {}
        for i in range(roomnum):
            result[roomnum] = [0, 0, 0, 0, 0, 0, 0]  # 开关次数, 使用时长, 总费用, 调度次数, 详单数, 调温次数, 调风次数
        for key in keys:
            perroomdata = sort[key]
            minutesDiff = 0  # 存放空调总运行时间,单位分钟
            price = 0.0  # 存放最终的价格
            dispatchnum = 0  # 存放调度次数
            changetem = 0  # 调温总次数
            changewind = 0  # 调风次数

            opentimes = 0  # 开关次数
            detailnum = len(perroomdata)  # 详单数

            pretem = 25  # 上一次的目标温度,初始为默认温度,或者零也可当作开机就是一次调温
            prewind = 0  # 上次风速
            for data in perroomdata:
                # 获得最后总金额
                price += data[5]
                # 获得最后总时长
                ta = time.strptime(data[2].split('.')[0], "%Y-%m-%d %H:%M:%S")
                tb = time.strptime(data[1].split('.')[0], "%Y-%m-%d %H:%M:%S")
                y, m, d, H, M, S = ta[0:6]
                dataTimea = datetime.datetime(y, m, d, H, M, S)
                y, m, d, H, M, S = tb[0:6]
                dataTimeb = datetime.datetime(y, m, d, H, M, S)
                # 两者相加得转换成分钟的时间差
                secondsDiff = (dataTimea - dataTimeb).seconds
                daysDiff = (dataTimea - dataTimeb).days
                # 两者相加得转换成分钟的时间差
                minutesDiff += daysDiff * 1440 + round(secondsDiff / 60, 1)

                # 获得最后调度次数
                dispatchnum += data[8]
                # 获得最后调温次数
                if data[7] != pretem:
                    changetem += 1
                # 获取最后调风次数
                if data[3] != prewind:
                    changewind += 1
                prewind = data[3]
                pretem = data[7]

                # 获取开关次数,如果无调风,无调温,无调度说明由于开关
                if data[7] == pretem and data[3] == prewind and data[8] == 0:
                    opentimes += 1
            result[key] = [opentimes, minutesDiff, price, dispatchnum, detailnum, changetem, changewind]

        return result


class logindbHandler:
    def __init__(self, cursor, con):
        self.tbname = loginTableName
        self.cursor = cursor
        self.con = con
        if self.isExist("admin", "admin", 1) == -1:
            print("write admin")
            self.writeData("admin", "admin", 1)

        if self.isExist("bar", "bar", 2) == -1:
            print("write bar")
            self.writeData("bar", "bar", 2)

        if self.isExist("manager", "manager", 3) == -1:
            print("write manager")
            self.writeData("manager", "manager", 3)

    def hashencode(self, password: str) -> str:
        return str(base64.b64encode(bytes(password, encoding="utf-8")))

    def gensessionid(self):
        session = md5(str(time.time()).encode('utf-8'))
        session = session.hexdigest()
        return session

    def writeData(self, username: str, password: str, mode: int):
        password = self.hashencode(password)
        try:
            self.cursor.execute('insert into ' + self.tbname + ' values' + '("' + username + '","' + password + '", ' + str(mode) + ')')
            self.con.commit()

        except Exception as e:
            print("注册部分写数据失败", e)
            raise Exception

    # 判断是否有该用户
    def isExist(self, username: str, password: str, mode: int):
        print("{} {} {}".format(username, password, mode))
        password = self.hashencode(password)
        try:
            self.cursor.execute("select * from " + self.tbname + " where username = " + '"' + username + '" and password = ' + '"' + password + '"' + ' and mode = ' + str(mode))
            query_result = self.cursor.fetchall()
            self.con.commit()

            # 有相应的用户数据,返回sessionid
            if len(query_result) != 0:
                # print(query_result)
                ret = self.gensessionid()
                print(ret)
                return ret
            else:
                # 无相应的用户数据
                print(-1)
                return -1
        except Exception as e:
            print("loginhandler数据库读取失败:", e)
            raise Exception


'''
 create table airinfo2(
    roomid int not null, 
    starttime date not null,
    endtime date not null,
    windspeed int not null,
    price real not null,
    mode int ,
    ratio real not null,
    aimtemproture int not null,
    isdispatch int not null,
    primary key (roomid, starttime));
# userid int not null,
'''

'''
# mode标识其级别
create table userinfo(
    username varchar(20) primary key not null,
    password varchar(20) not null,
    mode int not null);
'''
