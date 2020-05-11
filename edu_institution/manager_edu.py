# -*- coding: utf-8 -*-
import json,time,os,redis
import requests
import schedule
import threading,datetime
import traceback

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Sequence, MetaData, Table
from sqlalchemy.orm import relationship, sessionmaker
from logconfs.config import log
from rediscluster import StrictRedisCluster
from logconfs.con_vars import conf
from crawl_dazhong import Wxgzh_DaZhong
from crawl_meituan import Wxgzh_MeiTuan
from crawl_quanguo import Wxgzh_QuanGuo
from crawl_jiaoyubao import Wxgzh_JiaoYuBao
from crawl_zhonghua import Wxgzh_ZhongHua
from down_2_mysql import save_quanguo_toall,save_four_toall,ZhongHuaKaoShi,QuanGuoXiaoWai,JiaoYuBao,XueXiPeiXun,redisconn1

redisconn1.set("adv:edu",1577767397.0)

def get_hz_ip():
    url=conf["kuai_proxy"]["hz_url"]
    ip=requests.get(url).text
    ip_full = ip+",浙江省杭州市"
    redisconn1.set("adv:WechatSpider", ip_full)
    return ip

def get_ip():
    ip_full = json.loads(requests.get(conf["kuai_proxy"]["get_url"]).text)[
        "data"]["proxy_list"][0]
    ip = ip_full.split(",")[0]
    redisconn1.set("adv:WechatSpider", ip_full)
    return ip


def crawl():#
    cates_xuexi = {"2": "运动培训","3": "自习室","4": "书法培训", "6": "语言培训", "7": "音乐培训", "8": "美术培训", "10": "教育院校",
                  "11": "职业培训", "12": "升学辅导", "13": "留学", "14": "兴趣生活"}
    cates_qinzi = {"1": "亲子活动", "7": "儿童乐园", "15": "手工DIY", "16": "科普场馆", "17": "采摘/农家乐"}
    # try:
    #     ip = get_ip()
    #     print(ip)
    #     Wxgzh_ZhongHua(ip, "", "").start_crawl()
    # except:
    #     print(traceback.format_exc())
    # save_four_toall(ZhongHuaKaoShi)
    # try:
    #     ip = get_ip()
    #     Wxgzh_QuanGuo(ip, "", "").start_crawl()
    # except:
    #     pass
    # save_quanguo_toall(QuanGuoXiaoWai)
    # try:
    #     ip = get_ip()
    #     Wxgzh_JiaoYuBao(ip, "", "").start_crawl()
    # except:
    #     pass
    # save_four_toall(JiaoYuBao)
    # try:
    #     ip=get_hz_ip()
    #     Wxgzh_DaZhong(ip, "", "").start_crawl()
    # except:
    #     print(traceback.format_exc())
    #     pass
    # try:
    #     ip = get_ip()
    #     # ip="115.209.213.254:16578"
    #     print(ip)
    #     Wxgzh_MeiTuan(ip, cates_qinzi, "").start_crawl2()
    # except:
    #     print(traceback.format_exc())
    try:
        ip=get_ip()
        # ip='115.207.80.243:18481'
        print(ip)
        Wxgzh_MeiTuan(ip, cates_xuexi, "").start_crawl("")
    except:
        print(traceback.format_exc())
    # save_four_toall(XueXiPeiXun)

if __name__ == '__main__':
    crawl()
    # print(get_ip())
    # schedule.every().day.at("15:25:00").do(crawl)
    # while True:
    #    schedule.run_pending()
#react > div > div > div.center-content.clearfix > div.left-content > nav > ul > li.pagination-item.select.num-item > a
#react > div > div > div.center-content.clearfix > div.left-content > nav > ul > li.pagination-item.select.num-item > a
#react > div > div > div.center-content.clearfix > div.left-content > nav > ul > li.pagination-item.select.num-item > a
#react > div > div > div.center-content.clearfix > div.left-content > nav > ul > li:nth-child(7) > a
#react > div > div > div.center-content.clearfix > div.left-content > nav > ul > li:nth-child(4) > a