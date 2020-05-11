# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import time

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import csv
import os
from logconfs.con_vars import conf
import schedule
class JiFangSpider():
    def __init__(self):
        self.url="http://customer.netbank.cn/#/login"
        User_Agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0"]
        options = webdriver.ChromeOptions()
        options.add_argument('User-Agent=' + random.choice(User_Agents))
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options, executable_path='./chromedriver.exe')
        self.driver.get(self.url)

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                             "#app > div > div.login-con > div.form-con > form > div:nth-child(1) > div > div > input"))).send_keys(
        conf['jifang']['account'])
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                             "#app > div > div.login-con > div.form-con > form > div:nth-child(2) > div > div > input"))).send_keys(
        conf['jifang']['pwd'])
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                             "#app > div > div.login-con > div.form-con > form > div:nth-child(4) > div > button > span"))).click()

        cookies = self.driver.get_cookies()
        dicts = {i["name"]: i["value"] for i in cookies}
        # "X-OverrideGateway": proxy_ip_port,
        self.session = requests.session()
        self.session.cookies.clear()
        # session.proxies = {"http": "http://%s" % self.ip, "https": "http://%s" % self.ip}
        self.session.cookies = requests.utils.cookiejar_from_dict(dicts, cookiejar=None, overwrite=True)
    def send_weixin(self,msg):
        corp_id =conf['jifang']['corp_id']
        secret =conf['jifang']['secret']
        agent_id =int(conf['jifang']['agent_id'])
        party_id =conf['jifang']['party_id']
        tag_id =conf['jifang']['tag_id']
        accesstoken = json.loads(requests.get(
            'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s' % (corp_id, secret)).text)[
            "access_token"]
        data = {
            "touser": "liushaotian|rongxuewen|hushaojun|wangning|jiangdong",
            # "touser": "zhushixin",
            "msgtype": "text",
            "agentid": agent_id,
            "text": {
                "content": msg
            },
            "safe": 0,
            "party": party_id,
            "tag": tag_id
        }
        send_url = '{url}/cgi-bin/message/send?access_token={token}'.format(
            url="https://qyapi.weixin.qq.com", token=accesstoken)
        response = requests.post(url=send_url, data=bytes(json.dumps(data, ensure_ascii=False), 'utf-8'))
    def get_content(self,url,machine):
        headers={"Pragma":"no-cache","Cache-Control":"no-cache","Accept":"application/json, text/plain, */*","X-netbank-internal-key":"1","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36","Content-Type":"application/json;charset=utf-8","Referer":"http://customer.netbank.cn/","Accept-Encoding":"gzip, deflate","Accept-Language":"en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"}
        #"Connection":"keep-alive",
        res=self.session.get(url,headers=headers,verify=False)
        datas=json.loads(res.content.decode('utf8'))["data"]
        time_pre = str(datetime.datetime.now()).split(" ")[0]
        path = conf["logs"]["path_pre"] + time_pre+"\\" + machine
        if not os.path.exists(path):
            os.makedirs(path)

        timeArray = time.localtime(int(time.time()))
        otherStyleTime = time.strftime("%Y-%m-%d__%H.%M.%S__", timeArray)
        f = csv.writer(open(path + "\\" + otherStyleTime + machine+".csv", "w", newline=""))

        f.writerow(["time", "A电流", "A电压", "B电流", "A电压"])
        sumA=0
        sumB=0
        count=0
        for x in datas:
            sumA+=x["payload"]["A"]["电流"]
            sumB+=x["payload"]["B"]["电流"]
            count+=1
        sumA=round(sumA,2)
        sumB=round(sumB,2)
        avgA=round(sumA/count,2)
        avgB=round(sumB/count,2)
        for x in datas:
            f.writerow([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x["time"])),
                        x["payload"]["A"]["电流"],
                        x["payload"]["A"]["电压"],
                        x["payload"]["B"]["电流"],
                        x["payload"]["B"]["电压"]])
        f.writerow(["", "A电流总和"+str(sumA), "", "B电流总和"+str(sumB), ""])
        f.writerow(["", "A电流平均值"+str(avgA), "", "B电流平均值"+str(avgB), ""])
        machine_dicts={"18":"E-18","20":"E-20","24":"E-24","28":"C-28"}
        day=time.strftime("%Y-%m-%d", time.localtime(int(time.time())-86400))
        msg=machine_dicts[machine]+"\t"+day+"日\t"+"A电流总和:"+str(sumA)+"A\t"+"A电流平均值:"+str(avgA)+"A\t"+"B电流总和"+str(sumB)+"A\t"+"B电流平均值"+str(avgB)+"A"
        self.send_weixin(msg)
    def crawl_all(self):
        end = int(time.mktime(datetime.date.today().timetuple()))
        start=end-86400
        self.get_content('http://customer.netbank.cn/humiture/api/cabinet/internal/data?cabinetNum=FD01-E-18&start=%d&end=%d&type=electricity'%(start,end),'18')
        self.get_content('http://customer.netbank.cn/humiture/api/cabinet/internal/data?cabinetNum=FD01-E-20&start=%d&end=%d&type=electricity'%(start,end),'20')
        self.get_content('http://customer.netbank.cn/humiture/api/cabinet/internal/data?cabinetNum=FD01-E-24&start=%d&end=%d&type=electricity'%(start,end),'24')
        self.get_content('http://customer.netbank.cn/humiture/api/cabinet/internal/data?cabinetNum=FD01-C-28&start=%d&end=%d&type=electricity'%(start,end),'28')

if __name__ == '__main__':
    # schedule.every().day.at("22:18:05").do(JiFangSpider().crawl_all)
    # while True:
    #    schedule.run_pending()
    JiFangSpider().crawl_all()