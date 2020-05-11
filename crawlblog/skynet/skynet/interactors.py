import datetime
import json
import threading
import uuid
from abc import ABC
from dataclasses import dataclass

import redis
from scrapy import Spider

from skynet.skynet.models.task_info import TaskInfo, dict2task

que = []
tasks = []



class SpiderInteractor(object):  # 交互器
    def __init__(self, num=uuid.uuid1(), time=datetime.datetime.now()):
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.sem = threading.Semaphore(0)
        self.num = num
        self.time = time

    def wait_for_verify_code(self):
        """
        基于 task_info 获取独立的信号量，基于信号量等待进入等待，并且设立合理的超时时间
        :return: defered
        :rtype: Defered
        bytes: bytearray = None, verify_code_type=None, timeout=None
        """
        # signal = self.__get_signal__(task_info.task_id)
        # signal.wait(timeout)
        print("self.num",self.num)
        # self.sem.acquire(timeout=30)  # 内部维护的计数器减1，到0就会阻塞
        # self.r.publish('vrcode', json.dumps({'type': type, 'num': self.num}))
        pubsub = self.r.pubsub()
        pubsub.subscribe(['vrcode'])
        time_begin = datetime.datetime.now().minute
        for item in pubsub.listen():
            print(item, type(item))
            if json.loads(item["data"])["num"] == self.num and datetime.datetime.now().minute-30< time_begin:
                # self.sem.release()
                print("json.loads(item[\"data\"])[\"vrcode\"]", json.loads(item)["data"]["vrcode"])
                return json.loads(item["data"])["vrcode"]
            elif datetime.datetime.now().minute-30 > time_begin:
                # self.sem.release()
                return "timeout"
            else:
                return

    def wait_for_qr_code(self):
        """
        基于 task_info 获取独立的信号量，基于信号量等待进入等待，并且设立合理的超时时间
        :return: defered
        :rtype: Defered
        bytes: bytearray = None, verify_code_type=None, timeout=None
        """
        # self.sem.acquire(timeout=30)  # 内部维护的计数器减1，到0就会阻塞
        pubsub = self.r.pubsub()
        pubsub.subscribe(['qrcode'])
        time_begin = datetime.datetime.now().minute
        for item in pubsub.listen():
            print(item, type(item))
            if json.loads(item["data"])["num"] == self.num and datetime.datetime.now().minute-30< time_begin:
                # self.sem.release()
                # print("json.loads(item[\"data\"])[\"qrcode\"]", json.loads(item)["data"]["vrcode"])
                return json.loads(item["data"])["qrcode"]
            elif datetime.datetime.now().minute-30 > time_begin:
                # self.sem.release()
                return "timeout"
            else:
                return

    def report(self):
        print(str(len(que) / len(tasks) * 100) + "%")

    def __get_signal__(self, task_id):
        pass


def dict2spdinr(d):
    return SpiderInteractor()


class BaseSpider(Spider, ABC):
    def __init__(self, task_info: TaskInfo,
                 spider_context: SpiderInteractor, **kwargs):
        super().__init__()
        self.task_info = task_info
        self.spider_context = spider_context
    def start(self):
        # 返回deferred
        pass
    # def end(self):

    def resolvecode(self):  # 处理各种正确和错误流程
        pass



if __name__ == '__main__':
    # a=TaskInfo(taskid=1,infoid=1,task_name="a")
    T = json.loads('{"taskid":1,"infoid":1,"task_name":"firtst"}', object_hook=dict2task)
    # print(a.time)
    # print(a.task_name)
    # print(json.dumps())