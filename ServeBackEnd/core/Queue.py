import threading
import time

class Queue:
    def __init__(self, start):
        # running_list 列表里放的是列表类型，各元素对应着 房间号 请求开始响应的时间点 风速 温度 
        # waiting_list 各元素对应着房间号 开始被分配到等待队列的时间点 请求风速 请求温度
        self.running_list = []
        self.running_list2 = []
        self.waiting_list = []
        self.waiting_list2 = []
        self.start = start

    # !!!有三个监视函数要写
    # 1、等待队列里的等待时间超过两分钟就要调到running_list里
    # 2、运行队列里的空调有没有已经到达目标温度，到达之后自动停风
    # 3、到达目标后停风，如果温度差超过一度，就要自动开始送风
    # 因为是每分钟变化0.5度，超过一度自动发起请求，可以直接理解为调到waiting_list里

    def listenWaiting(self):
        end = time.process_time()
        t1 = end - self.start
        for i in range(len(self.waiting_list)):
            if t1 - self.waiting_list[i][1] >= 120:
                # 把原来在running_list的踢出去，
                self.running_list.sort(key=lambda x: x[1])
                temp_list = self.running_list.pop(0)
                self.running_list2.remove(temp_list[0])

                end = time.process_time()
                t2 = end - self.start
                temp_list[1] = t2
                self.waiting_list.append(temp_list)
                self.waiting_list2.append(temp_list[0])

                self.waiting_list2.remove(self.waiting_list[i][0])
                temp_list = self.waiting_list.pop(i)
                end = time.process_time()
                t3 = end - self.start
                temp_list[1] = t3
                self.running_list.append(temp_list)
                self.running_list2.append(temp_list[0])


class myThread1(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            self.queue.listenWaiting()
            time.sleep(0.5)


