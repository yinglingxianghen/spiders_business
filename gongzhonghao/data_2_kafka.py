# -*- coding: utf-8 -*-
from kafka import KafkaProducer
from kafka.errors import KafkaError
from logconfs_bak.con_vars import conf
import json

class Kafka_producer():
    '''
    使用kafka的生产模块
    '''
    def __init__(self, kafkatopic):
        self.kafkatopic = kafkatopic
        kafka_nodes = []
        for i in conf["kafka"]["servers"].split(","):
            kafka_nodes.append(i)
        self.producer = KafkaProducer(bootstrap_servers=kafka_nodes)

    def sendjsondata(self, params):
        try:
            parmas_message = json.dumps(params,ensure_ascii=False)
            producer = self.producer
            producer.send(self.kafkatopic,value=bytes(str(parmas_message),encoding='utf-8'))
            producer.flush()
        except KafkaError as e:
            pass

def send_to_kafka(msg):
    # 测试生产模块
    producer = Kafka_producer(conf["kafka"]["topic"])
    producer.sendjsondata(msg)
