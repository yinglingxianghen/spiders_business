#coding:utf8
from logconfs.con_vars import conf

import redis
[host,port]=conf["proxy"]["servers"].split(":")
redisconn1=redis.Redis(host=host,port=int(port),decode_responses=True)



print(redisconn1.get("adv:gongzhonghao"))
print(redisconn1.get("adv:WechatSpider"))

