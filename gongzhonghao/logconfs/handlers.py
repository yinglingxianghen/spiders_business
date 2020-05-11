import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
from logconfs.con_vars import conf

class Elk_producer(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.kafkatopic = conf["elk"]["topic"]
        kafka_nodes = []
        for i in conf["elk"]["servers"].split(","):
            kafka_nodes.append(i)
        self.producer = KafkaProducer(bootstrap_servers=kafka_nodes)

    def emit(self,record):
        try:
            msg = self.format(record)
            producer = self.producer
            producer.send(self.kafkatopic,value=msg.encode('utf-8'))
            producer.flush()
        except KafkaError as e:
            pass

    def close(self):
        logging.Handler.close(self)
