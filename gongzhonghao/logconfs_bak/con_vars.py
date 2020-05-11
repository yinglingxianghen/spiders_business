import configparser
import os

curpath = os.path.dirname(os.path.realpath(__file__))

cfgpath = os.path.join(curpath, "base_settings.ini")

# 创建管理对象
conf = configparser.ConfigParser()

# 读ini文件
conf.read(cfgpath, encoding="gbk")