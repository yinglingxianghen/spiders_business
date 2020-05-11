#coding:utf8
import logging.config
import logging.config,datetime,os

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../logs")

if not os.path.exists(log_path):
    os.makedirs(log_path)


logging.config.fileConfig(os.path.dirname(os.path.abspath(__file__))+"/log_conf.ini")

