#coding:utf8
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
from logconfs.con_vars import conf

class Elk_producer(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.kafkatopic = conf["kafka"]["topic_elk"]
        self.producer = KafkaProducer(bootstrap_servers=conf["kafka"]["server_elk"])

    def emit(self,record):
        try:
            msg = self.format(record)
            # msg1=json.loads(msg)
            # parmas_message = json.dumps(msg1,ensure_ascii=False)
            producer = self.producer
            producer.send(self.kafkatopic,value=msg.encode('utf-8'))
            producer.flush()
        except KafkaError as e:
            pass

    def close(self):
        logging.Handler.close(self)
