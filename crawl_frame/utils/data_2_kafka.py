#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import time


# from rediscluster import StrictRedisCluster
from rediscluster import RedisCluster


class Kafka_producer():
    '''
    使用kafka的生产模块
    '''

    def __init__(self, kafkahost, kafkaport, kafkatopic):
        self.kafkaHost = kafkahost
        self.kafkaPort = kafkaport
        self.kafkatopic = kafkatopic
        self.producer = KafkaProducer(bootstrap_servers='{kafka_host}:{kafka_port}'.format(
            kafka_host=self.kafkaHost,
            kafka_port=self.kafkaPort
        ))

    def sendjsondata(self, params):
        try:
            parmas_message = json.dumps(params)
            producer = self.producer
            producer.send(self.kafkatopic, parmas_message.encode('utf-8'))
            producer.flush()
        except KafkaError as e:
            print(e)


class Kafka_consumer():
    '''
    使用Kafka—python的消费模块
    '''

    def __init__(self, kafkahost, kafkaport, kafkatopic, groupid):
        self.kafkaHost = kafkahost
        self.kafkaPort = kafkaport
        self.kafkatopic = kafkatopic
        self.groupid = groupid
        self.consumer = KafkaConsumer(self.kafkatopic,
                                      bootstrap_servers='{kafka_host}:{kafka_port}'.format(
                                          kafka_host=self.kafkaHost,
                                          kafka_port=self.kafkaPort))

    def consume_data(self):
        try:
            for message in self.consumer:
                # print json.loads(message.value)
                yield message
        except KeyboardInterrupt as e:
            print(e)


def send_to_kafka(msg):
    '''
    测试consumer和producer
    :return:
    '''
    # 测试生产模块
    producer = Kafka_producer("192.168.50.233", 9092, "topic-pythonlog")
    producer.sendjsondata(msg)
    # for i in range(1):
    #     params ={'timestamp':'2019-10-15T18:15:31+08:00','host':'192.168.50.211','client_ip':'110.52.195.199','size':86,'response_time':0.016,'url':'/usercenter/api/v1/account/refreshtoken?refreshtoken=V2:829649EEAD14FE1E5803F93814099C8669A82FAE23945F6F','upstream_time':'0.016','upstream_host':'192.168.50.218:8989','http_host':'appapi-dev.safetree.com.cn','verb':'GET','uri':'/usercenter/api/v1/account/refreshtoken','xff':'110.52.195.199','referer':'','agent':'Mozilla/5.0 (Linux; Android 4.4.4; Lenovo K30-T Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Mobile Safari/537.36 safetreeapp/1.4.3.016','userid':'2029412281','comefrom':'20089','cookie':'','status':200}
    #     print(params)
    #     producer.sendjsondata(params)
    #     time.sleep(1)

if __name__ == '__main__':
    send_to_kafka({"a":"a","B":"b"})
    # import os
    # print(os.uname)
    # params ={'timestamp':'2019-10-15T18:15:31+08:00','host':'192.168.50.211','client_ip':'110.52.195.199','size':86,'response_time':0.016,'url':'/usercenter/api/v1/account/refreshtoken?refreshtoken=V2:829649EEAD14FE1E5803F93814099C8669A82FAE23945F6F','upstream_time':'0.016','upstream_host':'192.168.50.218:8989','http_host':'appapi-dev.safetree.com.cn','verb':'GET','uri':'/usercenter/api/v1/account/refreshtoken','xff':'110.52.195.199','referer':'','agent':'Mozilla/5.0 (Linux; Android 4.4.4; Lenovo K30-T Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Mobile Safari/537.36 safetreeapp/1.4.3.016','userid':'2029412281','comefrom':'20089','cookie':'','status':200}
    # print(type(params))