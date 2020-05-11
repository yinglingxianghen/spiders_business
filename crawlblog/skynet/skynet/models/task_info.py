import datetime
from dataclasses import dataclass


@dataclass
class TaskInfo(object):
    task_id: int
    info_id: int
    task_name: str
    time: datetime = datetime.datetime.now()


def dict2task(d):
    return TaskInfo(d['taskid'], d['infoid'], d['task_name'])
