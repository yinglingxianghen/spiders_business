import configparser
import os

curpath = os.path.dirname(os.path.realpath(__file__))

cfgpath = os.path.join(curpath, "base_settings.ini")
# print(cfgpath)  # cfg.ini的路径

# 创建管理对象
conf = configparser.ConfigParser()

# 读ini文件
conf.read(cfgpath, encoding="gbk")  # python3

# 获取所有的section
# sections = conf.sections()
# items = conf['ocean_account']["pwd"]
# print(items,type(items))
if __name__ == '__main__':
    for i in conf["mysql"]:
        print(i)