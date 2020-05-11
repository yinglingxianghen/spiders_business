# -*- coding: utf-8 -*-
import datetime
import json
import random

import redis
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import scrapy
import scrapy.crawler
import uuid
from skynet.skynet.interactors import BaseSpider, SpiderInteractor
from skynet.skynet.interactors import dict2task

class OceanengineItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()

# que = []
# tasks = []

from skynet.skynet.utils.save_to_txt import *
class OceanengineSpider(BaseSpider):
    name = 'oceanengine'
    allowed_domains = ['https://ad.oceanengine.com']
    start_urls = ['https://ad.oceanengine.com']
    print("--------------------------------------------------------")

    def __init__(self, task_info, spider_context,**kwargs):
        super(OceanengineSpider,self).__init__(task_info, spider_context, **kwargs)
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.num="001"
        self.type="vrcode001"

    def getcode(self):
        # self.spider_context.report()
        print("getcode")
        self.r.publish('vrcode', json.dumps({'type': self.type, 'num': self.num}))
        pubsub = self.r.pubsub()
        pubsub.subscribe(['vrcode'])
        time_begin = datetime.datetime.now().minute
        for item in pubsub.listen():
            print(item, type(item))
            if isinstance(item['data'],str):
                # self.sem.release()
                print("json.loads(item[\"data\"])[\"vrcode\"]", item['data'])
                return item['data']
            # if datetime.datetime.now().minute > time_begin:
            #     self.sem.release()
            #     return "timeout"
        # code=self.spider_context(num=uuid.uuid1(),type='vrcode').wait_for_verify_code()
        # print("getcode", code)
        # self.spider_context.report()
        # if code=='timeout':
        #     return "getvrtimeout"
        # return code

    def start_requests(self):    #登录
        User_Agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0"]
        url = "https://ad.oceanengine.com"
        options = webdriver.ChromeOptions()
        options.add_argument('User-Agent=' + random.choice(User_Agents))
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('window-size=1920x1480')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get(url)
        time.sleep(1)
        print(self.driver.title)

        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='login']/section/div[3]/div[4]/input"))).send_keys("1127597642@qq.com")
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='login']/section/div[3]/div[5]/input[1]"))).send_keys("AD.oceanengine123")

        #method2
        # WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='login']/section/div[3]/div[5]/input[2]/"))).send_keys("adafswer")
        # self.driver.execute_script('document.evaluate("//*[@id=\'login\']/section/div[3]/div[5]/input[1]",document).iterateNext().remove()')
        # b=OceanSpider(task_info=["001"]).parse()
        # b=input("请输入验证码:")
        b=self.getcode()
        # print(b,type(b))
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='login']/section/div[3]/div[6]/input"))).send_keys(b)
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='login']/section/div[3]/div[10]/div"))).click()
        time.sleep(1)
        cookies=self.driver.get_cookies()
        dict={}
        for i in cookies:
            dict[i["name"]] = i["value"]
        print(dict)
        headers={"X-OverrideGateway":"223.151.112.166:20652","Connection":"keep-alive","Sec-Fetch-Mode":"cors","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36","Accept":"*/*","Origin":"https://ad.oceanengine.com","Sec-Fetch-Site":"cross-site","Referer":"https://ad.oceanengine.com/pages/login/index.html","Accept-Encoding":"gzip, deflate, br","Accept-Language":"zh-CN,zh;q=0.9"}
        # cookies_jar = requests.cookies.RequestsCookieJar()
        # cookies_jar.set('sessionid', sessionid, domain='ad.oceanengine.com', path='/overture/cash/get_cash_flow')
        request=scrapy.Request(url="https://ad.oceanengine.com/overture/index/advertiser_chart/?st=2019-08-22&et=2019-08-28&_=1567064637411",headers=headers,cookies=dict,callback=self.parse)
        request.meta["proxy"]="http://127.0.0.1:8888"
        yield request
        headers = {"X-OverrideGateway": "113.128.122.249:21822", "Connection": "keep-alive", "Sec-Fetch-Mode": "cors",
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
                   "Content-Type": "application/x-www-form-urlencoded", "Accept": "*/*",
                   "Origin": "https://ad.oceanengine.com", "Sec-Fetch-Site": "cross-site",
                   "Referer": "https://ad.oceanengine.com/pages/login/index.html",
                   "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "zh-CN,zh;q=0.9"}

        session = requests.session()
        session.cookies.clear()
        session.proxies = {"http": "http://127.0.0.1:8888", "https": "http://127.0.0.1:8888"}
        res=requests.get("https://ad.oceanengine.com/overture/index/advertiser_chart/?st=2019-08-22&et=2019-08-28&_=1567064637411",headers=headers,cookies=dict)
        dump_all(res, n=3)
        #scrapy.Request(url, method='POST', body=json.dumps(my_data), headers={'Content-Type':'application/json'})

    def parse(self,response):
        print(response.text)
        # dump_all(response,n=1)

# if __name__ == '__main__':
    # process = scrapy.crawler.CrawlerProcess()
    # d=process.crawl(OceanengineSpider,task_info=json.loads('{"taskid":1,"infoid":1,"task_name":"second"}', object_hook=dict2task),spider_context=SpiderInteractor())
    # process.start()
