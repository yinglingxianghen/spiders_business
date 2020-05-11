import datetime
from dataclasses import dataclass
class Proxy(object):
    '''endpoint'''
    '''爬虫持续地爬取'''

@dataclass
class TaskInfo(object):
    # task_id: int
    # info_id: int
    # task_name: str
    # spider_name:str=None
    # # fromwhere:str
    # # increase:str
    # # intention:str
    # # lib:str
    # last_proxy:str=None
    # # account:str
    # time: datetime = datetime.datetime.now()
    def __init__(self,task_id,info_id,task_name,spider_name,last_proxy):
        '''

        :param task_id:
        :param info_id:
        :param task_name:
        :param spider_name:
        :param last_proxy:
        '''
        self.task_id=task_id
        self.info_id=info_id
        self.task_name=task_name
        self.spider_name=spider_name
        # fromwhere:str
        # increase:str
        # intention:str
        # lib:str
        self.last_proxy=last_proxy
        # account:str
        self.time=datetime.datetime.now()

def dict2task(d):
    return TaskInfo(d['taskid'], d['infoid'], d['task_name'],d["spider_name"],d["last_proxy"])