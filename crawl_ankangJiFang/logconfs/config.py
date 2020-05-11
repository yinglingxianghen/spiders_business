# -*- coding: utf-8 -*-
import logging
import os
import datetime
import os
from logconfs.json_formatter import JSONFormatter
from logconfs.con_vars import conf
# from interactors import project_dir
import uuid
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json

class Elk_producer(logging.Handler):
    def __init__(self, kafkatopic):
        logging.Handler.__init__(self)
        # self.kafkaHost = kafkahost
        self.kafkatopic = kafkatopic
        # self.producer = KafkaProducer(bootstrap_servers="192.168.50.233:9092")
        # self.producer = KafkaProducer(bootstrap_servers=[conf["kafka"]["server_elk1"], conf["kafka"]["server_elk2"],conf["kafka"]["server_elk3"]])
        self.producer = KafkaProducer(bootstrap_servers=conf["kafka"]["server_elk"])
        # self.producer = KafkaProducer(bootstrap_servers=["172.16.18.124:9092","172.16.18.125:9092","172.16.18.126:9092"])
    def emit(self,record):
        try:
            msg = self.format(record).replace("\'","\"")
            msg1=json.loads(msg)
            # msg1=json.loads(json.dumps(msg,ensure_ascii=False))
            parmas_message = json.dumps(msg1,ensure_ascii=False)
            #parmas_message = msg1
            producer = self.producer
            producer.send(self.kafkatopic,value=parmas_message.encode('utf-8'))
            # producer.send(self.kafkatopic,value=bytes(str(parmas_message),encoding='utf-8'))
            producer.flush()
        except KafkaError as e:
            pass

    # def emit(self,record):
    #     print("record",record.levelno)
    #     producer = Elk_producer("topic-wechat_logs")
    #     msg = self.format(record)
    #     producer.sendjsondata(msg)

    def close(self):
        # self.producer.stop()
        logging.Handler.close(self)

loggers={}
def log():
    global loggers
    time_pre = str(datetime.datetime.now()).split(" ")[0]
    print(time_pre)
    if loggers.get(time_pre):
        return loggers.get(time_pre)
    else:
        log = logging.getLogger(time_pre)
        log.setLevel(logging.DEBUG)
        # write log to file
        path=conf["logs"]["path_pre"]+time_pre
        if not os.path.exists(path):
            os.makedirs(path)
        handler = logging.FileHandler(path+ r'/base_code.log')
        handler.setLevel(logging.INFO)
        # write log to console
        handler_console = logging.StreamHandler()
        handler_console.setLevel(logging.INFO)
        # set formatter
        handler.setFormatter(JSONFormatter())
        handler_console.setFormatter(JSONFormatter("pretty"))
        # add handler
        # kah=Elk_producer("topic-crawledu_logs")
        kah = Elk_producer(conf["kafka"]["topic_elk"])
        log.addHandler(handler)
        log.addHandler(handler_console)
        log.addHandler(kah)
        loggers[time_pre]=log
        return log
# a='Traceback (most recent call last):n  File "/home/python/test_gongzhonghao/test_gongzhonghao_old.py", line 429, in start_crawln    self.crawl(3, s,obj2)n  File "/home/python/test_gongzhonghao/test_gongzhonghao_old.py", line 455, in crawln"one":'biz_detail_history_art_list>div:nth-child(%d)>div.article-contents>div>div.article-item-tilte.clearfix>div.pull-left>div>a'%(j)})n  File "/home/python/test_gongzhonghao/test_gongzhonghao_old.py", line 113, in wait_for_onen    EC.presence_of_element_located((By.CSS_SELECTOR, value))):n  File "/home/python/envwxgzh/lib/python3.7/site-packages/selenium/webdriver/support/wait.py", line 80, in untiln    raise TimeoutException(message, screen, stacktrace)nselenium.common.exceptions.TimeoutException: Message: nnnDuring handling of the above exception, another exception occurred:nnTraceback (most recent call last):n  File "/home/python/test_gongzhonghao/test_gongzhonghao_old.py", line 432, in start_crawln    "logname": self.logname, "origin_host": self.origin_host})n  File "/usr/local/python3/lib/python3.7/logging/__init__.py", line 1390, in warningn    self._log(WARNING, msg, args, **kwargs)n  File "/usr/local/python3/lib/python3.7/logging/__init__.py", line 1514, in _logn    self.handle(record)n  File "/usr/local/python3/lib/python3.7/logging/__init__.py", line 1524, in handlen    self.callHandlers(record)n  File "/usr/local/python3/lib/python3.7/logging/__init__.py", line 1586, in callHandlersn    hdlr.handle(record)n  File "/usr/local/python3/lib/python3.7/logging/__init__.py", line 894, in handlen    self.emit(record)n  File "/home/python/test_gongzhonghao/logconfs/config.py", line 24, in emitn    msg1=json.loads(msg.replace("'",""")) if "'" in msg else msgn  File "/usr/local/python3/lib/python3.7/json/__init__.py", line 348, in loadsn    return _default_decoder.decode(s)n  File "/usr/local/python3/lib/python3.7/json/decoder.py", line 337, in decoden    obj, end = self.raw_decode(s, idx=_w(s, 0).end())n  File "/usr/local/python3/lib/python3.7/json/decoder.py", line 353, in raw_decoden obj, end = self.scan_once(s, idx)njson.decoder.JSONDecodeError: Expecting ',' delimiter: line 1 column 70 (char 69)n'
