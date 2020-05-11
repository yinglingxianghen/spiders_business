import configparser
import os

curpath = os.path.dirname(os.path.realpath(__file__))

cfgpath = os.path.join(curpath, "base_settings.ini")
print(cfgpath)  # cfg.ini的路径

# 创建管理对象
conf = configparser.ConfigParser()

# 读ini文件
conf.read(cfgpath, encoding="utf-8")  # python3

# 获取所有的section
sections = conf.sections()

items = conf['ocean_account']["pwd"]
print(items,type(items))  # list里面对象是元