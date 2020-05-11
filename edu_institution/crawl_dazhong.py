# -*- coding: utf-8 -*-
import datetime

from lxml import etree
import requests,redis
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
from down_2_mysql import save_meituan_xuexipeixun,redisconn1,save_img,save_video
import uuid, json,telnetlib
from PIL import Image
from io import BytesIO

class Wxgzh_DaZhong():
    def __init__(self, ip, cates, acco):
        self.cates=cates
        self.redisconn1 = redisconn1
        self.url = "http://www.dianping.com/hangzhou"
        self.first=True
        # self.url = "http://www.dianping.com/hangzhou/ch75/g2873"
        requests.adapters.DEFAULT_RETRIES = 1
        self.session = requests.session()
        # self.session.keep_alive = False
        self.ip =ip
        self.session.proxies = {"http": "http://%s" % self.ip, "https": "http://%s" % self.ip}
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(
            'User-Agent=Mozilla/5.0 (Windows NT 15.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36')
        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_experimental_option("excludeSwitches",["ignore-certificate-errors", "safebrowsing-disable-download-protection",
                                              "safebrowsing-disable-auto-update","disable-client-side-phishing-detection"])
        self.options.add_argument('--profile-directory=Default')
        self.options.add_argument("--incognito")
        self.options.add_argument("--disable-plugins-discovery")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("disable-infobars")
        self.options.add_argument('--proxy-server=%s' % self.ip)
        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options, executable_path=conf["driver"]["driver_path"])



    def get_ip(self):
        url = conf["kuai_proxy"]["hz_url"]
        ip = requests.get(url).text
        ip_full = ip + ",浙江省杭州市"
        redisconn1.set("adv:WechatSpider", ip_full)
        return ip

    def test_ip(self, server):
        ip, port = server.split(":")[0],int(server.split(":")[1])
        try:
            telnetlib.Telnet(ip, port, timeout=30)
            return True
        except:
            return False

    def start_crawl(self):
        counts=0
        self.driver.set_page_load_timeout(10)
        try:
            self.driver.get('http://www.dianping.com/hangzhou/education')
        except Exception as e:
            pass
        # time.sleep(3)
        cates = ["g2872", "g2873", "g2876", "g2874", "g2878", "g179", "g260", "g33757", "g34129", "g32722", "g34107",
                 "g34302", "g2882"]
        lists = []
        for k in cates:
            for j in range(50):
                self.driver.set_page_load_timeout(10)
                try:
                    self.driver.get('http://www.dianping.com/hangzhou/ch75/%sp%d'%(k,j+1))
                except:
                    pass
                # self.driver.find_element_by_xpath('/html/body/div[2]/div[1]/ul/li[1]/div[1]/a[1]').click()
                # self.driver.switch_to.window(self.driver.window_handles[1])
                # time.sleep(2)
                # if len(adv):
                #     adv[0].click()
                try:
                    onepage = re.findall(
                    r'<a onclick="LXAnalytics\(\'moduleClick\', \'shoppic\'\)\" target="_blank" href="(.*?)" data-click-name="shop_img_click"',
                    self.driver.page_source)
                except:
                    continue
                #print("onepage", onepage)
                if onepage == lists:
                    break
                lists = onepage
                for l in onepage:
                    #print("dot")
                    dazhong_veri=True
                    if self.first==True:
                        self.driver.set_page_load_timeout(30)
                    else:
                        self.driver.set_page_load_timeout(4)
                    if self.test_ip(self.ip) == True:
                        #print("1111")
                        try:
                            self.driver.get(l)
                            self.first=False
                        except:
                            pass
                        try:
                            assert self.driver.page_source
                        except:
                            #print("verifalse")
                            dazhong_veri=False
                    else:
                        #print("3333")
                        self.driver.quit()
                        self.ip = self.get_ip()
                        self.options.add_argument('--proxy-server=%s' % self.ip)
                        self.driver = webdriver.Chrome(options=self.options,executable_path=conf["driver"]["driver_path"])
                        continue
                    if dazhong_veri==False or "验证中心" in self.driver.page_source:
                        log.warning({"msg": "", "mark": "出现验证码","service":"EduSquare","logname": "大众"})
                        self.driver.quit()
                        ip = self.get_ip()
                        # cates=self.cates[1:]
                        # #print("cates",cates)
                        self.options.add_argument('--proxy-server=%s' %ip)
                        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
                        self.driver = webdriver.Chrome(options=self.options,executable_path=conf["driver"]["driver_path"])
                        self.first=True
                        self.driver.get('http://www.dianping.com/')
                        continue
                    phone = re.findall(r'<span class="item J-phone-hide" data-phone="(.*?)">', self.driver.page_source)
                    phone = phone[0] if len(phone) else ""
                    area = re.findall(r' <span class="item">地址：</span>([\s\S]*?)</div>', self.driver.page_source)
                    area = area[0].strip() if len(area) else ""
                    name = re.findall(r'<h1>(.*?)</h1>', self.driver.page_source)
                    name = name[0].strip() if len(name) else ""
                    if name == "":
                        #print("2222")
                        # time.sleep(random.choice([3.1,2.3,2.8]))
                        continue
                    districts = ["市辖区", "上城区", "下城区", "江干区", "拱墅区", "西湖区", "滨江区", "萧山区", "余杭区", "经济技术开发区", "风景名胜区",
                                 "桐庐县", "淳安县", "大江东产业集聚区", "建德市", "富阳市", "临安市"]
                    dis = re.findall(r'<div class="breadcrumb">([\s\S]*?)</div>', self.driver.page_source)
                    dis = dis[0] if len(dis) else ""
                    for ii in districts:
                        if ii in dis:
                            district = ii
                            break
                        else:
                            district = ""
                    province = "浙江"
                    city = "杭州"
                    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    save_meituan_xuexipeixun(name, area, phone, dt, province, city, district,None,None)
                    files = re.findall(r'<div class="thumb">([\s\S]*?)</div>', self.driver.page_source)
                    # #print(files)
                    if len(files):
                        files = files[0]
                        video = re.findall(r'data-video="([\s\S]*?)">', files)
                        if len(video):
                            print("video",video)
                            save_video(name, area, video, dt)
                        imgs = re.findall(r'<img src="(.*?)" alt="', files)
                        if len(imgs):
                            for i in imgs:
                                print("imgs",imgs)
                                save_img(name, area, i, dt)
                    log.info({"msg": "success" + "大众|" + name + "|" + area + "|" + phone + "|" + dt, "mark": "爬取成功一篇", "service": "EduSquare", "logname": "大众"})
                    counts+=1
                    # time.sleep(random.choice([3.1,2.3,2.8]))

        self.driver.quit()
        if counts<30:
            log.error({"msg": "fail", "mark": "爬取不够",
                      "service": "EduSquare", "logname": "大众"})

