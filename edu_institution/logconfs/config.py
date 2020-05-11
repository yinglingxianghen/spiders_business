#coding:utf8
import logging.config
import logging.config,datetime,os
from logconfs.con_vars import conf

time_pre = str(datetime.datetime.now()).split(" ")[0]
path=conf["logs"]["path_pre"]
if not os.path.exists(path):
    os.makedirs(path)
logging.config.fileConfig(r"log_conf.ini")
log = logging.getLogger()