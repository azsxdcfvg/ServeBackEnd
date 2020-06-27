from .Aircon import *


class Afterend:
    def __init__(self):
        print("空调主控机初始化")
        self.myaircon = Aircon()

        # 开启线程3,负责检测房间是否要自动停风或送风
        print("开启线程3: 检测房间温度是否需要自动停风或送风")
        self.thread3 = myThread3(self.myaircon)
        self.thread3.run()


if __name__ == '__main__':
    myend = Afterend()