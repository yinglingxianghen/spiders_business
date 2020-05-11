# -*- coding: utf-8 -*-
import datetime
import urllib

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
from down_2_mysql import  save_quanguoxiaowai,redisconn1
import uuid,json,redis
from verify_code import getcode
class Wxgzh_QuanGuo():
    def __init__(self,ip,targ,acco):
        self.url = "http://xwpx.emis.edu.cn/omsweb/org/query/page"
        requests.adapters.DEFAULT_RETRIES = 1
        self.session = requests.session()
        self.session.keep_alive = False
        self.ip = ip
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
            log.info({"msg": self.ip, "mark": "代理过期重申", "service": "EduSquare", "logname": "全国"})
        else:
            self.ip = self.redisconn1.get("adv:WechatSpider").split(",")[0]
            log.info({"msg": self.ip, "mark": "代理过期复用", "service": "EduSquare", "logname": "全国"})

        self.session.proxies = {"http": "http://%s" % self.ip, "https": "http://%s" % self.ip}
    def start_crawl(self):
        counts=0
        self.driver.implicitly_wait(30)
        self.driver.delete_all_cookies()
        self.driver.get(self.url)
        self.driver.get(self.url)
        cookies = self.driver.get_cookies()
        dicts = {i["name"]: i["value"] for i in cookies}
        self.session.cookies = requests.utils.cookiejar_from_dict(dicts, cookiejar=None, overwrite=True)#"X-OverrideGateway":self.ip,

        dup=[]
        districts={"市辖区":330101,"上城区":330102,"下城区":330103,"江干区":330104,"拱墅区":330105,"西湖区":330106,"滨江区":330108,"萧山区":330109,"余杭区":330110,"经济技术开发区":330118,"风景名胜区":330119,"桐庐县":330122,"淳安县":330127,"大江东产业集聚区":330128,"建德市":330182,"富阳市":330183,"临安市":330185}

        for key,value in districts.items():
            for i in range(50):
                headers = {"Content-Type": "application/x-www-form-urlencoded",
                           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
                           "Accept": "*/*", "Sec-Fetch-Site": "same-site", "Sec-Fetch-Mode": "cors",
                           "Referer": "http://xwpx.emis.edu.cn/omsweb/org/query/page",
                           "Origin": "http://xwpx.emis.edu.cn", "Accept-Encoding": "gzip, deflate, br",
                           "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"}

                # self.session.keep_alive = False
                # from requests.adapters import HTTPAdapter
                # from urllib3.util import Retry
                # retry = Retry(connect=1, backoff_factor=5)
                # adapter = HTTPAdapter(max_retries=retry)
                # self.session.mount('http://', adapter)
                # self.session.mount('https://', adapter)
                try:
                    content = self.session.get("http://xwpx.emis.edu.cn/omsweb/captcha.jpg", headers=headers, verify=False,timeout=30).content

                except Exception as e:
                    self.update_proxy()
                    time.sleep(3)
                    continue
                with open("code.jpg", "wb") as f:
                    f.write(content)
                # urllib.request.urlretrieve("http://xwpx.emis.edu.cn/omsweb/captcha.jpg", "local-filename.jpg")
                code = getcode("code.jpg")
                data = {"province": "330000", "city": "330100", "district": str(value), "orgName": "", "legalCode": "1008001",
                        "pageNo":i, "pageSize": "", "code": code}
                try:
                    res1 = self.session.post("http://xwpx.emis.edu.cn/omsweb/org/query/page", headers=headers, data=data,verify=False, timeout=60).text
                    if res1 == "" or "System error" in res1 or "系统出错" in res1:
                        self.update_proxy()
                        continue
                except Exception as e:
                    self.update_proxy()
                    continue

                res=re.findall(r'<a href="#" onclick="viewDetail\((\d+)\)', res1)
                if res==dup:
                    break
                dup=res
                #print("res",res)
                if len(res):
                    for i in res:
                        headers1={"Connection":"keep-alive","Content-Length":"11","Cache-Control":"max-age=0","Origin":"http://xwpx.emis.edu.cn","Upgrade-Insecure-Requests":"1","Content-Type":"application/x-www-form-urlencoded","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3","Referer":"http://xwpx.emis.edu.cn/omsweb/org/query/page","Accept-Encoding":"gzip, deflate","Accept-Language":"en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"}
                        data1={"orgId":int(i)}
                        try:
                            res2 = self.session.post("http://xwpx.emis.edu.cn/omsweb/org/query/info", headers=headers1,
                                                     data=data1, verify=False, timeout=30).text
                            if res2 == "" or "System error" in res2 or "系统出错" in res2:
                                log.warning({"msg": "", "mark": "内容出错"+ res2, "service": "EduSquare", "logname": "全国"})

                                self.update_proxy()
                                continue
                        except Exception as e:
                            self.update_proxy()
                            continue

                        name=re.findall(r'<p class="panelbody-p fontsize18">([\s\S]+?)</p>', res2)
                        if len(name):
                            name=name[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        else:
                            continue
                        shelishijian=re.findall(r'设立时间：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        #print("shelishijian",shelishijian)
                        tongyidaima=re.findall(r'统一社会信用代码：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        if tongyidaima=="是":
                            tongyidaima="办理中"
                        zhucedizhi=re.findall(r'注册地址：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        area=re.findall(r'实际经营地址：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        farendaibiaoxingming=re.findall(r'法定代表人姓名：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        xiaozhangfuzeren=re.findall(r'校长\(负责人\)姓名：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        jubanzhemingcheng=re.findall(r'举办者名称\(姓名\)：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        jubanzheshuxing=re.findall(r'举办者属性：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')

                        banxuezizhi=re.findall(r'办学资质说明：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        banxuexukezhenghao=re.findall(r'办学许可证号：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        fazhengjiguan=re.findall(r'发证机关：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        farendengjibumen=re.findall(r'法人登记部门：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')

                        peixunleibie=re.findall(r'培训类别：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        peixunneirong=re.findall(r'培训内容：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        jianzhumianji=re.findall(r'建筑面积\(平方米\)：([\s\S]+?)<', res2)[0].replace('\n', '').replace('\t', '').replace('\r', '')
                        province = "浙江"
                        city = "杭州"
                        district=key
                        phone=""
                        #print("------------------------------------")
                        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        save_quanguoxiaowai(name=name,shelishijian=shelishijian,tongyidaima=tongyidaima,zhucedizhi=zhucedizhi,peixunneirong=peixunneirong,area=area,farendaibiaoxingming=farendaibiaoxingming,xiaozhangfuzeren=xiaozhangfuzeren,jubanzhemingcheng=jubanzhemingcheng,jubanzheshuxing=jubanzheshuxing,banxuezizhi=banxuezizhi,banxuexukezhenghao=banxuexukezhenghao,fazhengjiguan=fazhengjiguan,farendengjibumen=farendengjibumen,peixunleibie=peixunleibie,jianzhumianji=jianzhumianji,addtime=dt,province=province,city=city,district=district,phone=phone)
                        log.info({"msg":"success" + "全国" +"|"+i+shelishijian+"|"+tongyidaima +"|"+ zhucedizhi+"|"+ dt, "mark": "爬取成功", "service": "EduSquare", "logname": "全国"})

                        counts+=1
                        # time.sleep(1)
        self.driver.quit()
        if counts<1:

            log.info({"msg":"没爬够","mark": "出错报警","service": "EduSquare", "logname": "全国"})


if __name__ == '__main__':
    Wxgzh_QuanGuo("","","").start_crawl()

# import urllib.request
# url = driver.find_element_by_id("captcha").get_attribute("src")
# urllib.request.urlretrieve("http://xwpx.emis.edu.cn/omsweb/captcha.jpg", "local-filename.jpg")http://xwpx.emis.edu.cn/omsweb/captcha.jpg