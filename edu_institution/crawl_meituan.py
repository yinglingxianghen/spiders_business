# -*- coding: utf-8 -*-
import datetime
import telnetlib

from lxml import etree
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
from down_2_mysql import save_meituan_xuexipeixun,redisconn1,save_img,save_video
import uuid,json,redis
from PIL import Image
from io import BytesIO
class Wxgzh_MeiTuan():
    def __init__(self,ip,cates,cates2):
        # redis_nodes1 = [{'host': conf['proxy']['host1'], 'port': int(conf['proxy']['port1'])},
        #                 {'host': conf['proxy']['host1'], 'port': int(conf['proxy']['port2'])},
        #                 {'host': conf['proxy']['host1'], 'port': int(conf['proxy']['port3'])},
        #                 {'host': conf['proxy']['host1'], 'port': int(conf['proxy']['port4'])}]
        # self.redisconn1 = StrictRedisCluster(startup_nodes=redis_nodes1, decode_responses=True)
        self.redisconn1 = redisconn1
        self.url = "https://hz.meituan.com/"
        requests.adapters.DEFAULT_RETRIES = 1
        self.session = requests.session()
        self.session.keep_alive = False
        self.ip =self.test_and_reget_ip(ip)
        self.session.proxies = {"http": "http://%s"%self.ip,"https": "http://%s"%self.ip}
        self.options = webdriver.ChromeOptions()
        # self.options = webdriver.FirefoxOptions()
        self.options.add_argument('User-Agent=Mozilla/5.0 (Windows NT 15.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36')

        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        # self.options.add_argument('--headless')
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_experimental_option("excludeSwitches",
                                        ["ignore-certificate-errors", "safebrowsing-disable-download-protection","safebrowsing-disable-auto-update", "disable-client-side-phishing-detection"])
        self.options.add_argument('--profile-directory=Default')
        self.options.add_argument("--incognito")
        self.options.add_argument("--disable-plugins-discovery")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("disable-infobars")
        # self.options.add_argument("user-data-dir={}".format(userProfile))/60.182.197.159:18307
        self.options.add_argument("--proxy-server=http://%s"%self.ip)
        self.driver = webdriver.Chrome(options=self.options, executable_path=conf["driver"]["driver_path"])
        self.cates=cates

    def test_and_reget_ip(self,ip):
        host, port = ip.split(":")[0], ip.split(":")[1]
        resu = requests.get(""+host+":"+port)

        if list(json.loads(resu.text)["data"].values())[0] == False:

            return self.get_ip()
        return ip


    def get_ip(self):
        ip_full = json.loads(requests.get(conf["kuai_proxy"]["get_url"]).text)[
            "data"]["proxy_list"][0]
        ip = ip_full.split(",")[0]
        self.redisconn1.set("adv:WechatSpider", ip_full)
        return ip

    def test_ip(self, proxy):
        ip, port = proxy.split(":")[0],int(proxy.split(":")[1])
        try:
            telnetlib.Telnet(ip, port, timeout=30)
            return True
        except:
            return False

    def start_crawl(self,page_no):
        self.driver.get(self.url)
        self.driver.refresh()
        url1='https://hz.meituan.com/s/%E5%AD%A6%E4%B9%A0%E5%9F%B9%E8%AE%AD/'
        for key,value in list(self.cates.items()):
            try:
                self.driver.get(url1)
                assert self.driver.page_source
            except:
                self.driver.quit()
                ip = self.get_ip()
                self.options.add_argument("--proxy-server=http://%s" % ip)
                self.driver = webdriver.Chrome(options=self.options, executable_path=conf["driver"]["driver_path"])
                self.driver.get(self.url)
                self.driver.refresh()
                self.driver.get(url1)
            while True:
                mouse =WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#react > div > div > div.center-content.clearfix > div.left-content > div.filter-box > div.filter-section-wrapper > div:nth-child(1) > div.tags > div > div:nth-child(16) > a > span")))
                if mouse:
                   break
            time.sleep(3)
            ActionChains(self.driver).move_to_element(mouse).perform()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="react"]/div/div/div[2]/div[1]/div[1]/div[1]/div[2]/div/div/div[%s]/a/span' % key))).click()
            print("self.cates", self.cates)
            self.onepage()
            for i in range(50):
                try:
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                    '#react > div > div > div.center-content.clearfix > div.left-content > nav > ul > li.pagination-item.next-btn.active > a'))).click()
                    self.onepage()
                except:
                    print("oneerror",traceback.format_exc())
                    break

            print("pop_before_cates", self.cates)
            self.cates.pop(key)
            print("pop_after_cates",self.cates)
        self.driver.quit()

    def continue_crawl2(self,url_zhong):
        self.driver.get(self.url)
        self.driver.refresh()
        self.driver.get(url_zhong)
        self.onepage2()
        for i in range(50):
            try:
                WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                '#react > div > div > div.center-content.clearfix > div.left-content > nav > ul > li.pagination-item.next-btn.active > a'))).click()
                time.sleep(1)
                self.onepage2()
            except:
                print(traceback.format_exc())
                break
        self.start_crawl2()

    def start_crawl2(self):
        self.driver.get(self.url)
        self.driver.refresh()
        url2 = 'https://hz.meituan.com/qinzi/'
        for key, value in list(self.cates.items()):
            self.driver.get(url2)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH,'//*[@id="react"]/div/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[2]/div/div[%s]/a/span' %key))).click()
            time.sleep(1)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH,'//*[@id="react"]/div/div/div[2]/div[1]/div[1]/div[3]/div[1]/div[2]/div/div[%s]/a/span' % key))).click()
            time.sleep(1)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH,'//*[@id="react"]/div/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[2]/div/div[%s]/a/span' % key))).click()
            time.sleep(1)
            # with open("meituanyudnong.txt", "w", encoding="utf-8") as f:
            #     f.write(self.driver.page_source)
            self.cates.pop(key)
            self.onepage2()
            for i in range(50):
                try:
                    WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                    '#react > div > div > div.center-content.clearfix > div.left-content > nav > ul > li.pagination-item.next-btn.active > a'))).click()
                    time.sleep(1)
                    self.onepage2()
                except:
                    print(traceback.format_exc())
                    break
        self.driver.quit()

    def input(self):
        image = self.driver.find_element_by_css_selector('#yodaImgCode').screenshot_as_png
        im = Image.open(BytesIO(image))
        im.save('example.png')
        from verify_code import getcode
        code = getcode('example.png')
        self.driver.find_element_by_css_selector('#yodaImgCodeInput').send_keys(code)
        self.driver.find_element_by_css_selector('#yodaImgCodeSure').click()
        time.sleep(1)

    def myHandler(self,signum, frame):
        self.driver.execute_script('window.stop()')

    def onepage(self):
        counts=0
        time.sleep(2)
        for i in range(32):
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH,
                '//*[@id="react"]/div/div/div[2]/div[1]/div[2]/div[2]/div[%d]/div/div/a'%(i+1)))).click()
            except:
                break

            self.driver.set_page_load_timeout(30)
            try:
                self.driver.switch_to.window(self.driver.window_handles[1])
            except:
                self.driver.execute_script('window.stop()')
            proxy_valid = self.test_ip(self.ip)
            page_valid = True
            try:
                assert self.driver.page_source
            except:
                page_valid = False
            if not proxy_valid or not page_valid:
                print("proxy_valid",proxy_valid)
                print("page_valid",page_valid)
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.ip = self.get_ip()
                self.logmsg("info",self.ip,"代理过期重申")

                page_no = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                '#react > div > div > div.center-content.clearfix > div.left-content > nav > ul > li.pagination-item.select.num-item'))).text
                print("url_zhong",page_no)
                self.driver.quit()

                self.options.add_argument("--proxy-server=http://%s" % self.ip)
                self.driver = webdriver.Chrome(options=self.options, executable_path=conf["driver"]["driver_path"])
                self.driver.get(self.url)
                self.driver.refresh()
                url1 = 'https://hz.meituan.com/s/%E5%AD%A6%E4%B9%A0%E5%9F%B9%E8%AE%AD/'
                self.driver.get(url1)
                print("getnewurl")

                while True:
                    mouse = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                                 "#react > div > div > div.center-content.clearfix > div.left-content > div.filter-box > div.filter-section-wrapper > div:nth-child(1) > div.tags > div > div:nth-child(16) > a > span")))
                    if mouse:
                        break
                time.sleep(3)
                ActionChains(self.driver).move_to_element(mouse).perform()
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,
                '//*[@id="react"]/div/div/div[2]/div[1]/div[1]/div[1]/div[2]/div/div/div[%s]/a/span' % list(self.cates.keys())[0]))).click()
                print("self.cates", self.cates)
                while int(WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                '#react > div > div > div.center-content.clearfix > div.left-content > nav > ul > li.pagination-item.select.num-item'))).text) < int(page_no):
                    print(WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                    '#react > div > div > div.center-content.clearfix > div.left-content > nav > ul > li.pagination-item.select.num-item'))).text)
                    time.sleep(1)
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                    '#react > div > div > div.center-content.clearfix > div.left-content > nav > ul > li.pagination-item.next-btn.active > a'))).click()
                # return Wxgzh_MeiTuan(self.ip, self.cates, "").start_crawl(page_no)
                return self.onepage()

            str1 = re.findall(".push\((.*?)\);", self.driver.page_source)
            res0 = [i for i in str1 if "mapInfo" in i]
            if len(res0):
                res0 = res0[0]
            else:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                # time.sleep(random.choice([3.1, 2.3, 2.8]))
                continue
            name = json.loads(res0)['params']['shopInfo']['shopName']
            if name == "":
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                # time.sleep(random.choice([3.1, 2.3, 2.8]))
                continue
            phone = json.loads(res0)['params']['shopInfo']['phoneNo']
            address = json.loads(res0)['params']['shopInfo']['address']
            dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            lng = re.findall(r'"glng":(.+?),', self.driver.page_source)
            lat = re.findall(r'"glat":(.+?),', self.driver.page_source)
            lng =lng[0] if len(lng) else None
            lat =lat[0] if len(lat) else None
            #print("lng,lat", lng, lat)
            imgs = re.findall(r'<div class="img-item"(.*?)</div>', self.driver.page_source)
            imgs = list(set(imgs))
            if len(imgs):
                for i in imgs:
                    img = re.findall(r'\((.*?)\)', i)
                    if len(img):
                        save_img(name, address, img, dt)
            districts = ["市辖区", "上城区", "下城区", "江干区", "拱墅区", "西湖区", "滨江区", "萧山区", "余杭区", "经济技术开发区", "风景名胜区", "桐庐县",
                         "淳安县", "大江东产业集聚区", "建德市", "富阳市", "临安市"]
            for ii in districts:
                if ii in address:
                    district = ii
                    break
                else:
                    district = ""
            province = "浙江"
            city = "杭州"
            log.info({"msg":"success" + "美团|" + name + "|" + address + "|" + phone + "|" + dt, "mark": "爬取成功", "service": "EduSquare", "logname": "美团"})

            counts+=1
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
        if counts<1:
            log.error({"msg":"没爬够", "mark": "出错报警", "service": "EduSquare", "logname": "美团"})

            # time.sleep(random.choice([2.1, 2.3, 2.8]))

    def onepage2(self):
        counts=0
        for i in range(32):
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH,
                '//*[@id="react"]/div/div/div[2]/div[1]/div[2]/div[2]/div[%d]/div/div/a' % (i + 1)))).click()
            except:
                break

            self.driver.set_page_load_timeout(30)
            try:
                self.driver.switch_to.window(self.driver.window_handles[1])
            except:
                self.driver.execute_script('window.stop()')
            proxy_valid = self.test_ip(self.ip)
            page_valid=True
            try:
                assert self.driver.page_source
            except:
                page_valid=False
            if not proxy_valid or not page_valid:
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.ip = self.get_ip()
                self.logmsg("info", self.ip, "代理过期重申")

                url_zhong = self.driver.current_url
                self.driver.quit()
                return Wxgzh_MeiTuan(self.ip, self.cates, "").continue_crawl2(url_zhong)
            page = etree.HTML(self.driver.page_source)
            name = page.xpath('//*[@id="react"]/div/div/div[2]/div[1]/h1/text()')
            name = name[0] if len(name) else ""
            if name == "":
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                continue
            phone = page.xpath('//*[@id="react"]/div/div/div[2]/div[1]/div[2]/div[2]/span[2]/text()')
            phone = phone[0] if len(phone) else ""
            address = page.xpath('//*[@id="react"]/div/div/div[2]/div[1]/div[2]/div[1]/a/span/text()')
            address = address[0] if len(address) else ""
            dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            lng = re.findall(r'var lng = "(.+?)"', self.driver.page_source)
            lat = re.findall(r'var lat = "(.+?)"', self.driver.page_source)
            lng = lng[1] if len(lng) > 1 and '}' not in lng[1] else None
            lat = lat[1] if len(lat) > 1 and '}' not in lat[1] else None
            imgs = re.findall(r'<div class="img-item"(.*?)</div>', self.driver.page_source)
            imgs = list(set(imgs))
            if len(imgs):
                for i in imgs:
                    img = re.findall(r'\((.*?)\)', i)
                    if len(img):
                        save_img(name, address, img, dt)
            districts = ["市辖区", "上城区", "下城区", "江干区", "拱墅区", "西湖区", "滨江区", "萧山区", "余杭区", "经济技术开发区", "风景名胜区", "桐庐县",
                         "淳安县", "大江东产业集聚区", "建德市", "富阳市", "临安市"]
            for ii in districts:
                if ii in address:
                    district = ii
                    break
                else:
                    district = ""
            province = "浙江"
            city = "杭州"
            log.info({"msg":"success" + "美团|" + name + "|" + address + "|" + phone + "|" + dt, "mark": "爬取成功", "service": "EduSquare", "logname": "美团"})

            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            # time.sleep(random.choice([3.1, 2.3, 2.8]))
        if counts<1:
            log.error({"msg":"没爬够", "mark": "出错报警", "service": "EduSquare", "logname": "美团"})
