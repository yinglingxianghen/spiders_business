# coding:utf-8
import json, time, os, redis
import requests
import schedule
import threading, datetime
import traceback

from crawl_gongzhonghao import Wxgzh
from crawl_gongzhonghao import engine, Base, md, redisconn, redisconn1

from sqlalchemy import ForeignKey, Sequence, MetaData, Table
from sqlalchemy.orm import relationship, sessionmaker
from logconfs.config import logging
from rediscluster import StrictRedisCluster
from logconfs.con_vars import conf
log = logging.getLogger()
print("555555555555555555")

# 连接老公众号表
class Publicnumberlist(Base):

    __table__ = Table("publicnumberlist", md, autoload=True)


# 连接新公众号表
class Addlist(Base):
    __table__ = Table("addlist", md, autoload=True)


# 获取代理前预设时间点
redisconn1.set("adv:gongzhonghao", 1577767397)


# 获取新代理
def get_ip():
    ip_full = json.loads(
        requests.get(conf["kuai_proxy"]["get_url"]).text)["data"]["proxy_list"][0]
    print("ipppppppppppppp",ip_full)
    ip = ip_full.split(",")[0]
    redisconn1.set("adv:WechatSpider", ip_full)
    return ip

# 爬公众号
def craw(table):
    # 杀掉谷歌进程
    # os.system("ps -aux |grep chrome | awk '{print$2}'|xargs kill -9")

    accounts=conf["xigua_accounts"]["accounts"].split(',')
    # redisconn.lpush(conf["redis_acco"]["full_acco"],*accounts)
    print("ipkekkkkkkkkkkkkkkkk",redisconn.keys())
    redisconn.lpush("gongzhonghao_test:xigua_account","17091180890|20190890","13221016815|20196815")
    print("333333333333333333333333")
    for lostconnect in range(10):
        try:
            Session = sessionmaker(bind=engine)
            dbsession = Session()
            results = dbsession.query(table).order_by(table.id.desc()).all()
            print("4444444444444444444")
            # results = dbsession.query(table).all() #正向账号列表
            lists = []
            for r in results:
                lists.append(r.publicnumber)
            all_tarts = [lists[i:i + 50] for i in range(0, len(lists), 50)]
            print("aaaaaaaaaa",all_tarts)
            ip = get_ip()
            print("666666666666666666666")
            for i in all_tarts:
                account = redisconn.lrange(conf["redis_acco"]["full_acco"], all_tarts.index(i), all_tarts.index(i))[0]
                redisconn.sadd(conf["redis_acco"]["used_acco"], account)
                print("----------------------")
                threading.Thread(target=Wxgzh(ip, i, account).start_crawl_old).start() if table==Publicnumberlist else threading.Thread(target=Wxgzh(ip, i, account).start_crawl_new).start()
                print("=======================")

                time.sleep(30)
            break

        except Exception as e:
            print(traceback.format_exc())
            time.sleep(10)
            continue

if __name__ == '__main__':
    craw(Publicnumberlist)
    # schedule.every().day.at("16:46:00").do(craw,Addlist)
    # schedule.every().day.at("16:08:00").do(craw,Publicnumberlist)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
