# -*- coding: utf-8 -*-
import datetime
import requests
from rediscluster import StrictRedisCluster

requests.packages.urllib3.disable_warnings()
import os
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.action_chains import ActionChains
import pymysql
import schedule
import re
import kafka
import schedule
import time
import threading
import traceback
from logconfs.config import log
from logconfs.con_vars import conf
from collections import Counter
import random
from down_2_mysql import save_jioyubao,redisconn1,save_img
import uuid,json,redis

class Wxgzh_JiaoYuBao():
    def __init__(self,ip,cates,acco):
        self.url = "https://passport.jiaoyubao.cn/login/?jyb_url_callback=https%3A%2F%2Fhz.jiaoyubao.cn%2F"
        requests.adapters.DEFAULT_RETRIES = 1
        self.session = requests.session()
        self.session.keep_alive = False
        self.ip =ip
        self.session.proxies = {"http": "http://%s"%self.ip,"https": "http://%s"%self.ip}
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(
            'User-Agent=Mozilla/5.0 (Windows NT 15.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36')
        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument("--proxy-server=http://%s"%self.ip)
        self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options, executable_path=conf["driver"]["driver_path"])
        self.redisconn1 = redisconn1

    def get_ip(self):
        ip_full = json.loads(requests.get(conf["kuai_proxy"]["get_url"]).text)["data"]["proxy_list"][0]
        ip = ip_full.split(",")[0]
        self.redisconn1.set("adv:WechatSpider", ip_full)
        return ip

    def update_proxy(self):
        a = time.time()
        if a - int(float(self.redisconn1.get("adv:edu"))) > 300:
            self.ip = self.get_ip()
            self.redisconn1.set("adv:edu", a)
            log.warning({"msg": self.ip, "mark": "代理过期重申", "service": "EduSquare", "logname": "教育宝"})


        else:
            self.ip = self.redisconn1.get("adv:WechatSpider").split(",")[0]
            log.warning({"msg": self.ip, "mark": "代理过期复用", "service": "EduSquare", "logname": "教育宝"})
        self.session.proxies = {"http": "http://%s" % self.ip, "https": "http://%s" % self.ip}

    def start_crawl(self):
        counts=0
        self.driver.implicitly_wait(60)
        self.driver.delete_all_cookies()
        self.driver.get(self.url)
        WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[2]/div/div/div[1]/div[5]/a'))).click()
        time.sleep(0.5)
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#txtUserName'))).send_keys("13282027081")
        time.sleep(0.5)
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#txtPwd'))).send_keys("jygc2020")
        time.sleep(0.5)
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.newlogin-middle > div > div.newlogin-right.b-radius > div > div > a"))).click()
        headers={"Connection":"keep-alive","Upgrade-Insecure-Requests":"1","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36","Sec-Fetch-User":"?1","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3","Sec-Fetch-Site":"same-origin","Sec-Fetch-Mode":"navigate","Referer":"https://hz.jiaoyubao.cn/edu/","Accept-Encoding":"gzip, deflate, br","Accept-Language":"en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"}
        url1='https://hz.jiaoyubao.cn/wudaoxingti/'
        self.driver.get(url1)
        cookies = self.driver.get_cookies()
        dicts = {i["name"]: i["value"] for i in cookies}
        time.sleep(0.5)
        self.session.cookies = requests.utils.cookiejar_from_dict(dicts,cookiejar=None, overwrite=True)
        cates=["jueshiwu","dslingwu","jiewu","baleiwu","dupiwu","ladingwu","minzuwu","jianmeicao","xiandaiwu","gudianwu","yueqi","semspx","qsnmspx","shufameishu","caiyi","weiqi","xiangqi","guojixiangqi","guojitiaoqi","motepeixun","liyyipeixun","qiannengkaifa","shougong","xingqu","koucai","guoxue","shengyue","03sui","qinzileyuan","zaojiaotese","zhilikaifa","gantong","bantuoban","teshuzaojiao","mengshijiao","xiaoxue","shaoeryingyu","xialing","youxiaoxianjie","chuzhong","gaozhong","cjgk","ykpx","zizhuzhao","hanjiafudao","yasi","tuofu","shaoeryingyu","qingshao","apkao","kouyutingli","vip","xingainian","act","gre","sat","jianqiaoyingyu","xiaoyuzhong","liuxue","guojijiaoyu","yishuzuopin"]
        for k in cates:
            for j in range(100):
                #print("j",j)
                try:
                    res = self.session.get('https://hz.jiaoyubao.cn/%s/p%d.html'%(k,j+1), headers=headers,verify=False, timeout=8)
                    if res.text == "" or "System error" in res.text or "系统出错" in res.text:
                        self.update_proxy()
                        continue
                except Exception as e:
                    self.update_proxy()
                    continue
                time.sleep(0.5)
                onepage = re.findall(r'<a href="(.*?)" target="_blank" class="office-rlist-name" title="', res.text)
                if '没有找到' in res.text:
                    break
                for i in onepage:
                    url='https:'+i if "//" in i else 'https://hz.jiaoyubao.cn'+i
                    try:
                        res1=self.session.get(url,headers=headers,verify=False,timeout=8)
                        if res1.text == "" or "System error" in res1.text or "系统出错" in res1.text:
                            self.update_proxy()
                            continue
                    except Exception as e:
                        self.update_proxy()
                        continue
                    name=re.findall(r'【(.+?)】', res1.text)
                    name=name[0] if len(name) else ""
                    if name=="":
                        continue
                    area=re.findall(r'<p class="ellipsis-1 fl">([\s\S]+?)</p>', res1.text)
                    area=area[0].replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '') if len(area) else ""
                    phone=re.findall(r'<span name="span_tel_400">(.+?)\n', res1.text)
                    phone=phone[0].replace('</span>','').replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '') if len(phone) else ""
                    #print(name,area,phone)
                    lng = re.findall(r'var lng = "(.+?)"', res1.text)
                    lng=lng[0] if len(lng) else None
                    # print("lng",lng)
                    lat = re.findall(r'var lat = "(.+?)"', res1.text)
                    lat = lat[0] if len(lat) else None
                    # print("lat",lat)

                    img = re.findall(r'"images": \["(.*?)"],', res1.text)
                    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    if len(img):
                        for i in img[0].split(","):
                            img = i.replace('"', '')
                            save_img(name, area, img, dt)
                    districts = ["市辖区","上城区", "下城区", "江干区", "拱墅区", "西湖区", "滨江区", "萧山区", "余杭区", "经济技术开发区", "风景名胜区", "桐庐县",
                                 "淳安县", "大江东产业集聚区", "建德市", "富阳市", "临安市"]
                    dis = re.findall(r'<p class="ellipsis-1 fl">([\s\S]*?)</p>', res1.text)

                    dis = dis[0] if len(dis) else ""
                    for ii in districts:
                        if ii in dis:
                            district = ii
                            break
                        else:
                            district = ""
                    province = "浙江"
                    city = "杭州"
                    #name,area,phone,addtime,province,city,district,lng,lat)
                    save_jioyubao(name,area,phone,dt,province,city,district,lng,lat)
                    log.info({"msg": "success" + "教育宝" + "|" + name + "|" + area + "|" + phone, "mark": "出错告警", "service": "EduSquare", "logname": "教育宝"})
                    counts+=1
        self.driver.quit()
        if counts<20:
            log.error({"msg": "没爬够", "mark": "出错告警", "service": "EduSquare", "logname": "教育宝"})

if __name__ == '__main__':
    Wxgzh_JiaoYuBao("","","").start_crawl()
    # dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # save_meituan_xuexipeixun("name", "area", "phone", dt)
