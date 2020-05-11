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
from down_2_mysql import save_zhonghua,redisconn1,save_img
import uuid,json,redis
from lxml import etree
from selenium.webdriver.support.select import Select

class Wxgzh_ZhongHua():
    def __init__(self,ip,targ,acco):
        self.url = "https://kaoshi.china.com/edu/hz/"
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
        # self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options, executable_path=conf["driver"]["driver_path"])
        self.driver.maximize_window()
        self.redisconn1 = redisconn1
        self.web_targ = "zhonghua"
        self.tags = "edu1.0"
        self.logname = str(uuid.uuid1())
        self.origin_host =" self.get_realip()"

    def get_realip(self):
        filename = "ip.swbd"
        # open(filename, "w").write("")
        os.system("ifconfig > {}".format(filename))
        text = open("{}".format(filename)).read()
        ipv4 = re.findall(r'inet (.*?) netmask', text, re.S)[0]
        os.remove(filename)
        return ipv4

    def logmsg(self, grade, msg, mark):
        msg = msg.encode("gbk", 'ignore').decode("gbk", "ignore")
        mark = mark.encode("gbk", 'ignore').decode("gbk", "ignore")
        if grade == 'info':
            log.info({"msg": msg, "mark": mark, "web_targ": self.web_targ, "tags": self.tags, "logname": log.name,
                      "origin_host": self.origin_host, "level": "INFO"})
        elif grade == 'warning':
            log.warning({"msg": msg, "mark": mark, "web_targ": self.web_targ, "tags": self.tags, "logname": log.name,
                         "origin_host": self.origin_host, "level": "WARNING"})
        elif grade == 'error':
            log.error({"msg": msg, "mark": mark, "web_targ": self.web_targ, "tags": self.tags, "logname": log.name,
                       "origin_host": self.origin_host, "level": "ERROR"})
        else:
            pass

    def get_ip(self):
        ip_full = json.loads(
            requests.get(conf["kuai_proxy"]["get_url"]).text)[
            "data"]["proxy_list"][0]
        ip = ip_full.split(",")[0]
        self.redisconn1.set("adv:WechatSpider", ip_full)
        return ip
    def update_proxy(self):
        a = time.time()
        if a - int(float(self.redisconn1.get("adv:edu"))) > 300:
            self.ip = self.get_ip()
            self.redisconn1.set("adv:edu", a)
            self.logmsg("info",self.ip, "中华")
        else:
            self.ip = self.redisconn1.get("adv:WechatSpider").split(",")[0]
            self.logmsg("info",self.ip, "中华")
        self.session.proxies = {"http": "http://%s" % self.ip, "https": "http://%s" % self.ip}
    def start_crawl(self):
        counts=0
        self.driver.implicitly_wait(60)
        self.driver.delete_all_cookies()
        self.driver.get(self.url)
        cookies = self.driver.get_cookies()
        dicts = {i["name"]: i["value"] for i in cookies}
        time.sleep(0.5)
        headers={"Connection":"keep-alive","Upgrade-Insecure-Requests":"1","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36","Sec-Fetch-User":"?1","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3","Sec-Fetch-Site":"same-origin","Sec-Fetch-Mode":"navigate","Referer":"https://kaoshi.china.com/edu/hz/","Accept-Encoding":"gzip, deflate, br","Accept-Language":"en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"}
        self.session.cookies = requests.utils.cookiejar_from_dict(dicts,cookiejar=None, overwrite=True)
        oldurls = []
        cates=["peixun/tuozhan","peixun/zxx","peixun/fudao","peixun/yezj","peixun/yikao","peixun/shuhua","peixun/music","peixun/dance","peixun/qi","peixun/qiu","peixun/aihao","peixun/chinese","peixun/xiaoyu","pets/peixun","kouyu/peixun","toefl/peixun","ielts/peixun","catti/peixun","nce/peixun","waixiao/peixun","cet4/peixun","jianyan/peixun","sat/peixun","xly/peixun","dly/peixun","zuowen/peixun","children/peixun","ap/peixun","gmat/peixun","igcse/peixun","pte/peixun","al/peixun","al/peixun","tuoye/peixun","jianqiao/peixun","ssat/peixun","ib/peixun","aeas/peixun","aces/peixun","isee/peixun","qtlxks/peixun","peixun/chuguo","peixun/youxue","peixun/gjxx"]
        for k in cates:
            for j in range(100):
                try:
                    res = self.session.get('https://kaoshi.china.com/%s/hz/%d.htm'%(k,j+2), headers=headers,verify=False, timeout=8).text
                    if res == "":
                        self.update_proxy()
                        time.sleep(3)
                        continue
                except Exception as e:
                    self.logmsg(msg="error"+str(repr(traceback.format_exc())).replace("\"", "").replace("\'", ""), mark="")
                    self.update_proxy()
                    time.sleep(3)
                    continue
                #print("jjj", j)
                if "抱歉，没有找到相关课程" in res:
                    break
                # with open("0.txt", "w", encoding="utf-8") as f:
                #     f.write(res)

                onepage = re.findall(r'<span>机构：</span> <a href="(.*?)/">', res)
                onepage1 = list(set(onepage))
                for i in onepage1:
                    if i not in oldurls:
                        oldurls.append(i)
                        try:
                            res1 = self.session.get('https://kaoshi.china.com'+i, headers=headers,verify=False, timeout=8).text
                            res2 = self.session.get('https://kaoshi.china.com'+i+'/introduce/', headers=headers,verify=False, timeout=8).text
                            if res1 == "":
                                self.update_proxy()
                                time.sleep(3)
                                continue
                        except Exception as e:
                            self.logmsg(msg="error"+str(repr(traceback.format_exc())).replace("\"", "").replace("\'", ""), mark="")
                            self.update_proxy()
                            time.sleep(3)
                            continue
                        #print("iii",i)
                        res1=etree.HTML(res1)
                        with open("zhonghua.txt","w",encoding="utf-8") as f:
                            f.write(res2)
                        pics = re.findall(r'<figure>([\s\S]*?)</figure>', res2)
                        imgs = []
                        if len(pics):
                            for i in pics:
                                imgs.append(re.findall(r'<img src="(.*?)">', i)[0])
                        name = res1.xpath('/html/body/div[7]/div[1]/div[2]/p[3]/span[1]/text()')
                        if len(name):
                            for i in range(3,20):
                                name = res1.xpath('/html/body/div[7]/div[1]/div[2]/p[%d]/span[1]/text()'%i)
                                if name==[]:
                                    break
                                name=name[0] if len(name) else ""
                                area = res1.xpath('/html/body/div[7]/div[1]/div[2]/p[%d]/span[2]/text()'%i)
                                area=area[0] if len(area) else ""
                                phone = res1.xpath('/html/body/div[2]/div/span[1]/text()')
                                phone=phone[0] if len(phone) else ""
                                districts = ["市辖区", "上城区", "下城区", "江干区", "拱墅区", "西湖区", "滨江区", "萧山区", "余杭区",
                                             "经济技术开发区", "风景名胜区", "桐庐县", "淳安县", "大江东产业集聚区", "建德市", "富阳市", "临安市"]
                                for ii in districts:
                                    if ii in area:
                                        district = ii
                                        break
                                    else:
                                        district = ""
                                dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                province = "浙江"
                                city = "杭州"
                                save_zhonghua(name, area, phone, dt,province,city,district)
                                if len(imgs):
                                    for i in imgs:
                                        save_img(name,area,i,dt)

                                self.logmsg("info",msg="success" + "中华" + "|" + str(i) + name + "|" + area + "|" + phone + "|" + dt,mark="中华")
                                counts+=1
                                #print(name, area, phone)
                                time.sleep(1)
                        else:
                            for i in range(3, 20):
                                name = res1.xpath('/html/body/div[8]/div[1]/div[2]/p[%d]/span[1]/text()' % i)
                                if name == []:
                                    break
                                name = name[0] if len(name) else ""
                                if name=="":
                                    continue
                                area = res1.xpath('/html/body/div[8]/div[1]/div[2]/p[%d]/span[2]/text()' % i)
                                area = area[0] if len(area) else ""
                                phone = res1.xpath('/html/body/div[2]/div/span[1]/text()')
                                phone = phone[0] if len(phone) else ""

                                districts = ["市辖区", "上城区", "下城区", "江干区", "拱墅区", "西湖区", "滨江区", "萧山区", "余杭区",
                                             "经济技术开发区", "风景名胜区", "桐庐县","淳安县", "大江东产业集聚区", "建德市", "富阳市", "临安市"]
                                for ii in districts:
                                    if ii in area:
                                        district = ii
                                        break
                                    else:
                                        district = ""
                                province = "浙江"
                                city = "杭州"
                                dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                save_zhonghua(name, area, phone, dt,province,city,district)
                                if len(imgs):
                                    for i in imgs:
                                        save_img(name,area,i,dt)
                                log.info({"msg": "success" + "中华" + "|" + str(i) + name + "|" + area + "|" + phone + "|" + dt, "mark": "爬取成功", "service": "EduSquare", "logname": "中华"})

                                counts+=1
                                time.sleep(1)

        self.driver.quit()
        if counts<30:
            log.info({"msg":"没爬够","mark": "出错报警","service": "EduSquare", "logname": "中华"})

if __name__ == '__main__':
    Wxgzh_ZhongHua("","","").start_crawl()