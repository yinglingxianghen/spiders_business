# -*- coding: utf-8 -*-

import datetime
import requests
from rediscluster import StrictRedisCluster

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Sequence, MetaData, Table
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import exists
from logconfs.con_vars import conf

user = conf["mysql"]["user"]
pwd = conf["mysql"]["pwd"]
ip = conf["mysql"]["ip"]
port = conf["mysql"]["port"]
db = conf["mysql"]["db"]
engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (user, pwd, ip, port, db))
Base = declarative_base()
md = MetaData(bind=engine)
Session = sessionmaker(bind=engine)
dbsession = Session()

requests.packages.urllib3.disable_warnings()


class Hztest_addlist(Base):
    __table__ = Table("addlist", md, autoload=True)  # 自动加载表结构


class Publicnumberlist_copy1(Base):
    __table__ = Table("publicnumberlist", md, autoload=True)


class Whitelist_copy1(Base):
    __table__ = Table("whitelist", md, autoload=True)


class Operator_column(Base):
    __table__ = Table("operator_column", md, autoload=True)


class Operator(Base):
    __table__ = Table("operator", md, autoload=True)


redis_nodes = []
for i in conf["redis"]["servers"].split(","):
    print("Iiiiiiii",i)
    if i=="":
        break
    [host, port] = i.split(":")
    redis_nodes.append({'host': host, 'port': int(port)})
redisconn = StrictRedisCluster(startup_nodes=redis_nodes, decode_responses=True)

# import  redis
# [host,port]=conf["proxy"]["servers"].split(":")
# print("host",host,port)
# redisconn1=redis.Redis(host=host,port=int(port))


# print(redisconn1.get("adv:gongzhonghao"))
# print(redisconn1.get("adv:WechatSpider"))

# for i in conf["proxy"]["servers"].split(","):
#     if i == "":
#         break
#     [host, port] = i.split(":")
#     redis_nodes1.append({'host': host, 'port': int(port)})
[host,port]=conf["proxy"]["servers"].split(":")
redis_nodes1 = [{'host': host, 'port': int(port)}]
redisconn1 = StrictRedisCluster(startup_nodes=redis_nodes1, decode_responses=True)


print(redisconn1.get("adv:gongzhonghao"))
print(redisconn1.get("adv:WechatSpider"))

# print(redisconn1.get("adv:gongzhonghao"))
# print(redisconn1.get("adv:WechatSpider"))


requests.packages.urllib3.disable_warnings()
import os
import redis
from rediscluster import StrictRedisCluster
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
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Sequence, MetaData, Table
from sqlalchemy.orm import relationship, sessionmaker
from data_2_kafka import send_to_kafka
from logconfs.config import logging
from logconfs.con_vars import conf
from collections import Counter

# from gongzhonghao_new import Publicnumberlist_copy1, dbsession, redisconn, redisconn1
import random
import uuid, json
from logconfs.json_formatter import JSONFormatter

'''爬公众号'''


class Wxgzh(object):
    logger = logging.getLogger(__qualname__)

    def __init__(self, ip, targ, account):
        self.url = "http://data.xiguaji.com/Home#/Search/"
        requests.adapters.DEFAULT_RETRIES = 5
        self.session = requests.session()
        self.session.keep_alive = False
        self.ip = self.test_and_reget_ip(ip)

        self.session.proxies = {"http": "http://%s" % self.ip, "https": "http://%s" % self.ip}

        self.options = webdriver.ChromeOptions()
        self.options.add_argument(
            'User-Agent=Mozilla/5.0 (Windows NT 15.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36')
        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        # self.options.add_argument('--headless')

        self.options.add_argument("--proxy-server=http://%s" % self.ip)
        self.driver = ''

        self.account = account
        self.targets = targ

    # 测试当前代理，过期则重新获取代理
    def test_and_reget_ip(self, ip):
        resu = requests.get(conf["kuai_proxy"]["test_left_url"] + ip)
        if list(json.loads(resu.text)["data"].values())[0] == False:
            return self.get_ip()
        return ip

    # 获取新代理
    def get_ip(self):
        try:
            ip_full = json.loads(
                requests.get(conf["kuai_proxy"]["get_url"]).text)["data"]["proxy_list"][0]
        except:
            time.sleep(3)
            return self.get_ip()
        ip = ip_full.split(",")[0]
        redisconn1.set("adv:gongzhonghao", time.time())
        redisconn1.set("adv:WechatSpider", ip_full)
        return ip

    # 异步等待元素加载
    def wait_for_one(self, elements):
        for (key, value) in elements.items():
            if WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, value))):
                return key
            else:
                continue

    # 对每个p标签的内容做格式化处理
    def modify_span(self, single_str):
        if single_str == '':
            return ''
        else:
            tran_span = re.sub(
                "<em.*?>|</em>|<section.*?>|</section>|<p.*?>|</p>|<span.*?>|</span>|<strong.*?>|</strong>|<a.*?>|<img.*?>|<svg.*?>|</svg>|<animate.*?>|</animate>|<rect.*?>|</rect>",
                "", single_str)
            tran_span = re.sub('<br.*?>', '', tran_span)
            tran_span_right = '<p id="content" align="left">' + tran_span + '</p>'
            return tran_span_right

    # 得到每段的内容后格式化
    def join_span(self, list):
        return '<p id="content" align="left">' + ''.join(list) + '</p>'

    # 获取所有标签内内容
    def span_content(self, single_str):
        content = re.findall(r'>([^<].+?)<', single_str)
        return content if len(content) else []

    # 对每个图片标签的内容格式化处理
    def modify_img(self, single_str):
        tran_span_left = re.sub("data-src", 'src', single_str)
        tran_span_left = '<p id="content" align="left">' + tran_span_left + '</p>'
        return tran_span_left

    # 获取字符串在整个内容的所有索引列表
    def order_index(self, list, str1, ci):
        n = 0
        cis = []
        for i in range(ci):
            n = list.find(str1, n + 1)
            cis.append(n)
        return cis

    # 获取正确的文字和图片在整个内容的索引列表
    def word(self, html, span_index, spans_0, ci):
        span_o = dict(Counter(span_index))
        span_2 = [key for key, value in span_o.items() if value == ci]
        if span_2 == []:
            return span_index
        span_odata = dict(Counter(spans_0))
        span_2data = [key for key, value in span_odata.items() if value == ci]

        span_yuanindex = []
        span_dupindex = []

        for s in span_2:
            for index, data in enumerate(span_index):
                if data == s:
                    span_dupindex.append(index)
        span_chongindex = []  # 排序重复的索引列表
        for i in (span_dupindex[i + 1:i + ci] for i in range(0, len(span_dupindex), ci)):
            for j in i:
                span_chongindex.append(j)
        for data in span_2data:
            for ii in self.order_index(html, data, ci)[1:]:
                span_yuanindex.append(ii)
        for index, data in enumerate(span_chongindex):
            span_index[data] = span_yuanindex[index]
        return span_index

    # 将图片包括标签全部“|”格式化
    def change(self, value):
        length = len(value.group())
        lentlist = ['' for i in range(length)]
        return '|' + '|'.join(lentlist)

    # 处理内容格式化
    def resolve_content(self, htm):
        author = re.findall(r'<meta name="author" content="(.*?)">', htm)
        author = author[0] if len(author) else ""
        description = re.findall(r'<meta name="description" content="(.*?)"', htm)
        description = description[0] if len(description) else ""
        img0 = re.findall(r'var cover = "(.*?)";', htm) if htm else []
        html = re.findall(r'id="js_content"([\s\S]*?)nonce="', htm)
        html = html[0] if len(html) else ""
        if html == "":
            return "", "", "", "", ""

        htmls = re.findall(r">.*?<|img.*?>", html)
        htmls_clear = []
        for i in htmls:
            i = re.sub(r'>(.*?)<', '\\1', i)
            i = re.sub(r'(^img.*?)', '<' + '\\1', i)
            htmls_clear.append(i)
        # 得到所有的文字内容和img标签内容
        htmls_content = ''.join(htmls_clear)
        # 得到所有干净的文字内容

        htmls_ps = re.sub(r'<img.*?>', self.change, htmls_content)

        imgs = re.findall(r"<img[\s\S]*?>", html)
        img_count = len(imgs)

        if len(imgs) >= 3:
            imgs_three = ['http' + re.findall('http(.*?)"', i)[0] for i in imgs[:3] if 'http' in i]
        else:
            imgs_three = ['http' + re.findall('http(.*?)"', i)[0] for i in imgs if 'http' in i]

        imgs_0 = re.findall(r"<img[\s\S]*?>", html)
        imgs_index = [htmls_content.find(i) for i in imgs_0]
        img_correct = list(map(self.modify_img, imgs_0))
        img_correct = [i for i in img_correct if 'class="__bg_gif" border="0" vspace="0" data-ratio=' not in i]
        for i in range(2, 21, 1):
            imgs_index = self.word(htmls_content, imgs_index, imgs_0, i)
        # 将所有的section和p标签分段处理
        spans_origin = re.findall(r'<p[\s\S^/]+?</p>|<section.+?>[\s\S^/]*?</section>', html)
        # 如果带有图片，也分段处理
        spans_0 = []
        for i in spans_origin:
            section = re.sub(r'<img.*?>', '|img|', i)
            sections = section.split('|img|')
            for j in sections:
                spans_0.append(j)
        # 再对p标签中的span和strong内容分段处理
        spans_sec = []
        for i in spans_0:
            if '</p>' in i:
                ps = re.findall(r'<p[\s\S^/]*?</p>|<span[\s\S^/]*?</span>|<strong[\s\S^/]*?</strong>', i)
                for j in ps:
                    spans_sec.append(j)
            else:
                spans_sec.append(i)

        spans_content = list(map(self.span_content, spans_sec))
        # 删除空格
        for x in spans_content:
            while x.count('\u3000\u3000') > 0:
                x.remove('\u3000\u3000')
        while spans_content.count([]) > 0:
            spans_content.remove([])
        content_0 = [i[0] for i in spans_content]
        span_index = [htmls_ps.find(i) for i in content_0]
        # 重复20次得到准确的索引列表
        for i in range(2, 21, 1):
            span_index = self.word(htmls_ps, span_index, content_0, i)
        # 将文字和图片的内容和索引分别整合起来
        spans_z = list(map(self.join_span, spans_content))
        tags = img_correct + spans_z
        indexes = imgs_index + span_index
        he = zip(tags, indexes)
        he_end = [i[0] for i in sorted(he, key=lambda x: x[1])]
        img0 = '<p id="content" align="left"><img src="' + img0[0] + '"></p>' if len(
            img0) else ""
        end = img0 + '<p id="content" align="left"></p>'.join(he_end)
        # 对所得结果进行杂乱字符的清除
        end = re.sub('<p id="content" align="left">&nbsp;</p>|&nbsp;|<a.*?>|</a>|<span.*?>', '', end)
        end = re.sub(
            r'[^\u4e00-\u9fa5a-zA-Z0-9=\'"%@#$*()<>:^&!_\-． 。，、；：？！\\ˉˇ¨`~々～‖∶＂＇｀｜·…—‘’“”〝〞〔〕〈〉《》「」『』〖〗【】（）［］｛｝︻︼﹄﹃＋－×÷﹢﹣±／＝∥∠≌∽≦≧≒﹤﹥≈≡≠≤≥＜＞≮≯①②③④⑤⑥⑦⑧⑨⑩㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇.丶;?/]',
            "", end)
        return end, imgs_three, author, img_count, description

    # 登录
    def login(self):
        try:
            self.driver = webdriver.Chrome(chrome_options=self.options,
                                           executable_path=os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                                        conf["driver"]["driver_path"]))
            self.driver.get(self.url)
            time.sleep(2)
            self.driver.refresh()
            account = self.account.split("|")[0]
            pwd = self.account.split("|")[1]
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "#div_qrcode > div.phone-logon > form > div:nth-child(1) > input[type=text]"))).send_keys(
                account)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "#div_qrcode > div.phone-logon > form > div:nth-child(2) > input[type=password]"))).send_keys(
                pwd)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#div_qrcode>div.phone-logon>a.btn-logon-on.js-account-logon"))).click()
            try:
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         '#XiGuaDataPage > div.d-main.d-main-w.oooooo > div > div.query-item-list.clearfix.js-search-query > div.control-search-box > div.control-search-1.d-control-search > input[type=text]')))
            except:
                self.driver.refresh()

        except Exception as e:
            self.logger.warning({"mark": "首页打开失败重启", "msg": traceback.format_exc()})
            self.driver.close()
            self.ip = self.get_ip()
            self.options.add_argument("--proxy-server=http://%s" % self.ip)
            return self.login()

    # 搜索公众号
    def click_search(self, s):
        self.driver.implicitly_wait(60)
        if len(self.driver.find_elements_by_xpath('//*[@id="XiGuaDataPage"]/div[1]/div/div[2]/div[1]/div[1]/input')):

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="XiGuaDataPage"]/div[1]/div/div[2]/div[1]/div[1]/input'))).clear()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="XiGuaDataPage"]/div[1]/div/div[2]/div[1]/div[1]/input'))).send_keys(s)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="XiGuaDataPage"]/div[1]/div[1]/div/div[1]/a[1]'))).click()
        else:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="searchKey"]'))).clear()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="searchKey"]'))).send_keys(s)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="XiGuaDataPage"]/div[1]/div[1]/div/div[1]/a[1]'))).click()

    # 爬取老公众号主流程
    def start_crawl_old(self):
        print("++++++++++++++++++++++++++")
        # 爬取文章计数
        counts = 0
        self.logger.info({"mark": "新一轮列表循环开启"})
        self.login()
        for s in self.targets:
            try:
                self.logger.info({"mark": "此次爬取老公众号",
                                  "gongzhonghao": s})
                self.click_search(s)
                # 判断点击搜索后的页面显示
                if len(self.driver.find_elements_by_xpath(
                        '//*[@id="search-ressult-container"]/div/div[1]/div[1]/div[1]/div[2]/div[1]/h3')):
                    self.logger.info({"mark": "搜索后有文章列表开始爬取", "gongzhonghao": s})
                elif len(self.driver.find_elements_by_xpath('//*[@id="XiGuaDataPage"]/div[1]/div[2]/div/h6')) and \
                        WebDriverWait(
                            self.driver, 10).until(EC.presence_of_all_elements_located(
                            (By.XPATH, '//*[@id="XiGuaDataPage"]/div[1]/div[2]/div/h6')))[0].text == '抱歉，暂无搜索结果':
                    self.logger.warning({"mark": "没找到该公众号", "gongzhonghao": s})
                    self.driver.back()
                    continue


                elif len(self.driver.find_elements_by_xpath('//*[@id="XiGuaDataPage"]/div')) and \
                        WebDriverWait(self.driver, 10).until(
                                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="XiGuaDataPage"]/div')))[
                            0].text == '对不起，因为您的访问过于频繁，已经超过系统允许的访问次数，暂时无法使用该功能，请联系在线客服进行处理':

                    self.logger.warning({"mark": "此帐号被禁搜索", "msg": self.account,
                                         "gongzhonghao": s})
                    redisconn.lrem(conf["redis_acco"]["full_acco"], 0, self.account)
                    self.logger.info(
                        {"mark": "剩余完好账号有", "msg": redisconn.lrange(conf["redis_acco"]["full_acco"], 0, -1),
                         "gongzhonghao": s})
                    self.account = redisconn.lrange(conf["redis_acco"]["full_acco"], 0, -1)[-1]
                    assert len(redisconn.lrange(conf["redis_acco"]["full_acco"], 0, -1))
                    self.driver.quit()
                    return self.start_crawl()
                else:
                    break
                # 匹配查找第几个结果才是目标公众号
                getdao = False
                no = 0
                for match in range(1, 21):
                    match_accouts = self.driver.find_elements_by_xpath(
                        '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[1]/div[2]/div[1]/span[1]' % match)
                    if len(match_accouts):
                        try:
                            if match_accouts[0].text == s:
                                getdao = True
                                no = match
                                break
                            else:
                                continue
                        except Exception as e:
                            self.logger.warning({"mark": "没有精确匹配到", "msg": traceback.format_exc(),
                                                 "gongzhonghao": s})
                if getdao == True:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH,
                             '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[2]/div/a[1]' % no))).click()
                    if len(self.driver.find_elements_by_xpath(
                            '//*[@id="biz_detail_container"]/div/div[1]/div/div[1]/div[1]/div[2]/div[1]/h3')) == 0:
                        self.logger.warning({"mark": "此帐号详情按钮点不开已被封禁限制搜索", "msg": self.account,
                                             "gongzhonghao": s})
                        redisconn.lrem(conf["redis_acco"]["full_acco"], 0, self.account)
                        self.logger.warning(
                            {"mark": "剩余全部账号有", "msg": redisconn.lrange(conf["redis_acco"]["full_acco"], 0, -1),
                             "gongzhonghao": s})
                        assert len(redisconn.lrange(conf["redis_acco"]["full_acco"], 0, -1))
                        self.driver.quit()
                        return self.start_crawl()
                    # 查询公众号在老表中的数据
                    for lostconnect in range(50):
                        try:
                            # 查询老公众号在表中的这条记录
                            obj2 = dbsession.query(Publicnumberlist_copy1).filter(
                                Publicnumberlist_copy1.publicnumber == s).with_for_update(read=True).first()
                            break

                        except Exception as e:
                            dbsession.rollback()
                            self.logger.warning({"mark": "mysql连接失败", "msg": traceback.format_exc(),
                                                 "gongzhonghao": s})
                            time.sleep(3)
                            continue

                    if len(self.driver.find_elements_by_xpath(
                            '//*[@id="biz_detail_history_art_list"]/div[2]/div')) != 1:
                        try:
                            self.crawl(1, s, obj2)
                            self.crawl(2, s, obj2)
                            self.crawl(3, s, obj2)
                        except Exception as e:
                            self.logger.warning({"mark": "爬取异常", "msg": traceback.format_exc(),
                                                 "gongzhonghao": s})
                    elif len(WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located(
                            (By.XPATH, '//*[@id="biz_detail_history_art_list"]/div[2]/div')))) == 1:
                        try:
                            self.crawl(3, s, obj2)
                            self.crawl(4, s, obj2)
                            self.crawl(5, s, obj2)
                        except Exception as e:
                            self.logger.warning({"mark": "爬取异常", "msg": traceback.format_exc(),
                                                 "gongzhonghao": s})
                    else:
                        self.logger.warning({"mark": "其他第一行元素异常", "msg": traceback.format_exc(),
                                             "gongzhonghao": s})
                    self.driver.back()
                self.logger.info({"mark": "老公众号已成功爬完", "gongzhonghao": s})
            except Exception as e:
                self.logger.warning({"mark": "老公众号未成功爬完原因", "msg": traceback.format_exc(),
                                     "gongzhonghao": s})
                self.driver.back()
            counts += 1
            try:
                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR,
                     '#XiGuaDataPage > div.d-main.d-main-w.oooooo > div > div.query-item-list.clearfix.js-search-query > div.control-search-box > div.control-search-1.d-control-search > input[type=text]')))
            except:
                self.driver.quit()
                new_proxy = self.get_ip()
                self.options.add_argument("--proxy-server=http://%s" % new_proxy)
                self.login()

        self.driver.close()
        if counts < 1:
            self.logger.error({"mark": "爬取出错报警"})

    # 爬取新公众号主流程
    def start_crawl_new(self):
        counts = 0
        self.logger.info({"mark": "新一轮列表循环开启"})

        self.login()
        for s in self.targets:
            try:
                self.logger.info({"mark": "此次爬取新公众号",
                                  "gongzhonghao": s})

                self.click_search(s)
                if len(self.driver.find_elements_by_xpath(
                        '//*[@id="search-ressult-container"]/div/div[1]/div[1]/div[1]/div[2]/div[1]/h3')):
                    self.logger.info({"mark": "搜索后有文章列表开始爬取", "msg": "",
                                      "gongzhonghao": s})
                elif len(self.driver.find_elements_by_xpath('//*[@id="XiGuaDataPage"]/div[1]/div[2]/div/h6')) and \
                        WebDriverWait(
                            self.driver, 10).until(EC.presence_of_all_elements_located(
                            (By.XPATH, '//*[@id="XiGuaDataPage"]/div[1]/div[2]/div/h6')))[0].text == '抱歉，暂无搜索结果':
                    self.logger.warning({"mark": "没找到该公众号",
                                         "gongzhonghao": s})

                    self.driver.back()
                    continue

                elif len(self.driver.find_elements_by_xpath('//*[@id="XiGuaDataPage"]/div')) and \
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="XiGuaDataPage"]/div')))[
                            0].text == '对不起，因为您的访问过于频繁，已经超过系统允许的访问次数，暂时无法使用该功能，请联系在线客服进行处理':

                    self.logger.warning({"mark": "此帐号被禁搜索", "msg": self.account,
                                         "gongzhonghao": s})
                    redisconn.lrem(conf["redis_acco"]["full_acco"], 0, self.account)
                    self.logger.info(
                        {"mark": "剩余完好账号有", "msg": redisconn.lrange(conf["redis_acco"]["full_acco"], 0, -1),
                         "gongzhonghao": s})
                    self.account = redisconn.lrange(conf["redis_acco"]["full_acco"], 0, -1)[-1]
                    assert len(redisconn.lrange(conf["redis_acco"]["full_acco"], 0, -1))
                    self.driver.quit()
                    return self.start_crawl()
                else:
                    break
                getdao = False
                no = 0
                for match in range(1, 21):
                    match_accouts = self.driver.find_elements_by_xpath(
                        '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[1]/div[2]/div[1]/span[1]' % match)
                    if len(match_accouts):
                        try:
                            if match_accouts[0].text == s:
                                getdao = True
                                no = match
                                break
                            else:
                                continue
                        except Exception as e:
                            self.logger.warning({"mark": "没有精确匹配到", "msg": traceback.format_exc(),
                                                 "gongzhonghao": s})

                if getdao == True:
                    name = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[1]/div[2]/div[1]/h3' % no))).text
                    for lostconnect in range(50):
                        try:
                            public = dbsession.query(exists().where(Publicnumberlist_copy1.name == name)).scalar()
                            oper = dbsession.query(exists().where(Operator.name == name)).scalar()
                            oper_co = dbsession.query(exists().where(Operator_column.name == name)).scalar()
                            white = dbsession.query(exists().where(Whitelist_copy1.origin == name)).scalar()
                            break
                        except Exception as e:
                            self.logger.warning({"mark": "mysql连接失败", "msg": traceback.format_exc(), "gongzhonghao": s})

                            time.sleep(3)
                            continue
                    if public or oper or oper_co or white:
                        self.logger.info({"mark": "新公众号重复不爬", "gongzhonghao": s})

                        try:
                            dbsession.query(Hztest_addlist).filter(Hztest_addlist.publicnumber == s).delete()
                            dbsession.commit()
                            self.logger.info({"mark": "新公众号因重复已删", "gongzhonghao": s})
                        except Exception as e:
                            self.logger.warning(
                                {"mark": "sql删除重复公众号执行报错", "msg": traceback.format_exc(), "gongzhonghao": s})
                            dbsession.rollback()
                        self.driver.back()
                        continue
                    accounts = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[1]/div[2]/div[2]/span' % no))).text
                    if "第" and "名" in accounts:
                        if len(self.driver.find_elements_by_xpath(
                                '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[1]/div[2]/div[2]/span' % no)):
                            accounts = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.XPATH,
                                                                '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[1]/div[2]/div[2]/span' % no))).text
                        elif len(self.driver.find_elements_by_xpath(
                                '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[1]/div[2]/div[2]/span[2]' % no)):
                            accounts = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.XPATH,
                                                                '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[1]/div[2]/div[2]/span[2]' % no))).text
                        elif len(self.driver.find_elements_by_xpath(
                                '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[1]/div[2]/div[2]/span[3]' % no)):
                            accounts = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.XPATH,
                                                                '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[1]/div[2]/div[2]/span[3]' % no))).text
                        else:
                            accounts = "账号主体：未获取到"
                    body = accounts if "账号主体：" not in accounts else accounts.split("账号主体：")[1]
                    body = body if " " not in body else body.split(" ")[0]
                    introduction = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[1]/div[3]/div[1]/div[1]/p' % no))).text

                    avator = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[1]/div[1]/div/img' % no))).get_attribute(
                        "src")
                    with open("avator.jpg", "wb") as f:
                        f.write(requests.get(avator).content)

                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH,
                             '//*[@id="search-ressult-container"]/div/div[1]/div[%d]/div[2]/div/a[1]' % no))).click()

                    if len(self.driver.find_elements_by_xpath(
                            '//*[@id="biz_detail_container"]/div/div[1]/div/div[1]/div[1]/div[2]/div[1]/h3')) == 0:
                        self.logger.warning({"mark": "此帐号详情按钮点不开已被封禁限制搜索", "msg": self.account,
                                             "gongzhonghao": s})

                        redisconn.lrem(conf["redis_acco"]["full_acco"], 0, self.account)

                        self.logger.warning(
                            {"mark": "剩余全部账号有", "msg": redisconn.lrange(conf["redis_acco"]["full_acco"], 0, -1),
                             "gongzhonghao": s})

                        self.account = redisconn.lrange(conf["redis_acco"]["full_acco"], 0, -1)[-1]
                        assert len(redisconn.lrange(conf["redis_acco"]["full_acco"], 0, -1))
                        self.driver.quit()
                        return self.start_crawl()

                    try:
                        self.logger.info({"mark": "开始执行sql", "gongzhonghao": s})

                        obj1 = dbsession.query(Hztest_addlist).filter(Hztest_addlist.publicnumber == s).with_for_update(
                            read=True).first()
                        publicnumberlist = Publicnumberlist_copy1(name=name, publicnumber=s, company=body,
                                                                  description=introduction,
                                                                  categery1=obj1.categery1,
                                                                  categery2=obj1.categery2,
                                                                  categery3=obj1.categery3,
                                                                  decoder='Old', status=0)
                        dbsession.add(publicnumberlist)

                        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        whitelist_copy1 = Whitelist_copy1(origin=name, originType=0, addTime=dt)
                        dbsession.add(whitelist_copy1)

                        headers = {'platformSecret': conf["interp"]["secret"]}
                        body = {'username': name,
                                'intro': introduction[:64]}
                        files = {'headImage': open('avator.jpg', 'rb')}
                        res_jpg = requests.post(conf["interp"]["url"], headers=headers, data=body, files=files).text
                        if json.loads(res_jpg)['code'] == "200":
                            dbsession.query(Hztest_addlist).filter(Hztest_addlist.publicnumber == s).delete()
                            dbsession.commit()
                            self.logger.info({"mark": "新公众号sql执行完毕表插入成功", "gongzhonghao": s})
                        else:
                            dbsession.rollback()
                            self.driver.back()
                            self.logger.warning({"mark": "接口返回错误", "msg": res_jpg, "gongzhonghao": s})
                            continue

                    except Exception as e:
                        self.logger.warning({"mark": "sql执行报错", "msg": traceback.format_exc(), "gongzhonghao": s})
                        dbsession.rollback()
                        self.driver.back()
                        continue

                    for lostconnect in range(50):
                        try:
                            obj1 = dbsession.query(Publicnumberlist_copy1).filter(
                                Publicnumberlist_copy1.publicnumber == s).with_for_update(read=True).first()
                            break
                        except Exception as e:
                            self.logger.warning({"mark": "mysql连接失败", "msg": traceback.format_exc(),
                                                 "gongzhonghao": s})
                            dbsession.rollback()
                            time.sleep(5)
                            continue
                    if len(self.driver.find_elements_by_xpath(
                            '//*[@id="biz_detail_history_art_list"]/div[2]/div')) != 1:
                        try:
                            self.crawl(1, s, obj1)
                            self.crawl(2, s, obj1)
                            self.crawl(3, s, obj1)
                        except Exception as e:
                            self.logger.warning({"mark": "爬取异常", "msg": traceback.format_exc(),
                                                 "gongzhonghao": s})


                    elif len(WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located(
                            (By.XPATH, '//*[@id="biz_detail_history_art_list"]/div[2]/div')))) == 1:
                        try:
                            self.crawl(3, s, obj1)
                            self.crawl(4, s, obj1)
                            self.crawl(5, s, obj1)
                        except Exception as e:
                            self.logger.warning({"mark": "爬取异常", "msg": traceback.format_exc(),
                                                 "gongzhonghao": s})

                    else:
                        self.logger.warning({"mark": "其他第一行元素异常", "msg": traceback.format_exc(),
                                             "gongzhonghao": s})

                    self.driver.back()
                self.logger.info({"mark": "新公众号已成功爬完", "gongzhonghao": s})

            except Exception as e:
                self.logger.warning({"mark": "新公众号未成功爬完原因", "msg": traceback.format_exc(),
                                     "gongzhonghao": s})

                self.driver.back()
            counts += 1

        self.driver.quit()
        if counts < 1:
            self.logger.error({"mark": "爬取出错报警"})

    # 爬取每组公众号
    def crawl(self, j, s, obj2):
        try:
            found = self.wait_for_one({
                "multi": '#biz_detail_history_art_list>div:nth-child(%d)>div.article-contents>div:nth-child(1)>div.article-item-tilte.clearfix>div.pull-left>div>a' % (
                    j),
                "one": '#biz_detail_history_art_list>div:nth-child(%d)>div.article-contents>div>div.article-item-tilte.clearfix>div.pull-left>div>a' % (
                    j)})
        except:
            self.logger.warning({"mark": "元素未定位到",
                                 "gongzhonghao": s})
            return

        if found == 'one':
            lianjie = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@id="biz_detail_history_art_list"]/div[1]/div[2]/div/div[1]/div[1]/div/a'))).get_attribute(
                "href")
            headers = {"Accept": "application/json,text/javascript,*/*;q=0.01",
                       "User-Agent": "Mozilla/5.0(Windows NT 15.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
            res = self.session.get(lianjie, headers=headers, verify=False)
            content, imgs_three, author, img_count, description = self.resolve_content(res.text)

        elif found == 'multi':
            timestamp = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="biz_detail_history_art_list"]/div[%d]/div[1]/div[1]' % (j,)))).text.split("：")[1]
            timeArray = time.strptime(timestamp, "%Y/%m/%d %H:%M")
            timeStamp = int(time.mktime(timeArray))
            origin = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="biz_detail_container"]/div/div[1]/div/div[1]/div[1]/div[2]/div[1]/h3'))).text

            for i in range(10):
                try:
                    title = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH,
                                                                                                "//*[@id=\"biz_detail_history_art_list\"]/div[%d]/div[2]/div[%d]/div[1]/div[1]/div/a" % (
                                                                                                    j, i + 1)))).text
                    self.logger.info({"mark": "开始爬取新文章",
                                      "title": title, "gongzhonghao": s})

                    if redisconn.exists("title_" + title):
                        self.logger.info({"mark": "新文章由于标题重复跳过",
                                          "title": title, "gongzhonghao": s})
                        continue
                    lianjie = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH,
                                                                                                  "//*[@id=\"biz_detail_history_art_list\"]/div[%d]/div[2]/div[%d]/div[1]/div[1]/div/a" % (
                                                                                                      j,
                                                                                                      i + 1)))).get_attribute(
                        "href")
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36",
                        'Connection': 'close'}
                    self.session.keep_alive = False
                    from requests.adapters import HTTPAdapter
                    adapter = HTTPAdapter(max_retries=1)
                    self.session.mount('http://', adapter)
                    self.session.mount('https://', adapter)
                    try:
                        res = self.session.get(lianjie, headers=headers, verify=False, timeout=(3, 3))
                        if res.text == "" or "System error" in res.text or "系统出错" in res.text:
                            a = time.time()
                            if a - float(redisconn1.get("adv:gongzhonghao")) > 300:
                                self.ip = self.get_ip()
                                redisconn1.set("adv:gongzhonghao", a)
                                self.logger.info({"mark": "代理过期更换重申", "msg": redisconn1.get("adv:WechatSpider"),
                                                  "title": title, "gongzhonghao": s})
                            else:
                                self.ip = redisconn1.get("adv:WechatSpider").split(",")[0]
                                self.logger.info({"mark": "代理过期更换复用", "msg": redisconn1.get("adv:WechatSpider"),
                                                  "title": title, "gongzhonghao": s})

                            self.session.proxies = {"http": "http://%s" % self.ip, "https": "http://%s" % self.ip}
                            continue
                    except Exception as e:
                        print("rediserror",traceback.format_exc())
                        a = time.time()
                        if a - float(redisconn1.get("adv:gongzhonghao")) > 300:
                            self.ip = self.get_ip()
                            redisconn1.set("adv:gongzhonghao", a)
                            self.logger.info({"mark": "代理过期更换重申", "msg": redisconn1.get("adv:WechatSpider"),
                                              "title": title, "gongzhonghao": s})

                        else:
                            self.ip = redisconn1.get("adv:WechatSpider").split(",")[0]
                            self.logger.info({"mark": "代理过期更换复用", "msg": redisconn1.get("adv:WechatSpider"),
                                              "title": title, "gongzhonghao": s})

                        self.session.proxies = {"http": "http://%s" % self.ip, "https": "http://%s" % self.ip}
                        continue
                    try:
                        content, imgs_three, author, img_count, description = self.resolve_content(res.text)
                    except:
                        self.logger.info({"mark": "格式解析错误", "msg":traceback.format_exc(),
                                          "title": title, "gongzhonghao": s})
                        continue
                    author = re.sub(
                        r'[^\u4e00-\u9fa5a-zA-Z0-9=\'"%@#$*()<>:^&!_\-． 。，、；：？！\\ˉˇ¨`~々～‖∶＂＇｀｜·…—‘’“”〝〞〔〕〈〉《》「」『』〖〗【】（）［］｛｝︻︼﹄﹃＋－×÷﹢﹣±／＝∥∠≌∽≦≧≒﹤﹥≈≡≠≤≥＜＞≮≯①②③④⑤⑥⑦⑧⑨⑩㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇.丶;?/]',
                        "", author)
                    description = re.sub(
                        r'[^\u4e00-\u9fa5a-zA-Z0-9=\'"%@#$*()<>:^&!_\-． 。，、；：？！\\ˉˇ¨`~々～‖∶＂＇｀｜·…—‘’“”〝〞〔〕〈〉《》「」『』〖〗【】（）［］｛｝︻︼﹄﹃＋－×÷﹢﹣±／＝∥∠≌∽≦≧≒﹤﹥≈≡≠≤≥＜＞≮≯①②③④⑤⑥⑦⑧⑨⑩㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇.丶;?/]',
                        "", description)
                    if content == "" and imgs_three == "" and author == "" and img_count == "":
                        self.logger.info({"mark": "该文章内容为空跳过",
                                          "title": title, "gongzhonghao": s})
                        continue
                    guolv_content = ['掌门1对1', '理优1对1', '昂立嗨课堂', '学在家', '学而思', '大思英语', '博士老爸', '溢米辅导', '一米辅导', '学霸君1对1',
                                     '家有学霸', '三好网', '猿辅导', '小猿口算', '海风教育', '西瓜创客', '核桃编程', '编玩边学', '汤老师记忆法', '英语点点通',
                                     '邦元英语', '艾莉丝英语', '新助教育', '星时代教育', '新京报', '现代快报']
                    assert_content = True

                    for i0 in guolv_content:
                        if content.find(i0) != -1:
                            assert_content = False
                            break

                    if assert_content == False:
                        self.logger.info({"mark": "该文章内容有营销词跳过",
                                          "title": title, "gongzhonghao": s})
                        continue

                    lis = ["免费试学", "免费获取", "免费领", "免费听课", "立即报名", "即可报名", "爆款好课", "超值的活动", "即有机会获得", "即可获得", "参团",
                           "先抢先得"]
                    nums = []
                    if origin not in ["初中生学习方法", "小学学习资源库"]:
                        for ii in lis:
                            if origin.find(ii) != -1:
                                nums.append(origin.find(ii))
                    nums = sorted(nums)
                    if len(nums):
                        content = content[:nums[0]] + "</p>"
                    guolv = ['荐号', '限时特惠', '明日团', '返团', '福利', '专属', '粉丝福利', '开团', '爆款', '拼团', '团购', '截团', '报名', '最后一天',
                             '即将截止', '开放报名', '预告', '开课', '预售', '倒计时', '秒杀', '等你来领', '优惠券', '红包', '任性领', '立减', '立省',
                             '惠购', '划算', '最后X天', '性价比', '首发', '必买', '必入', '大放送', '限量', '礼包', '包邮', '开售', '免费领', '推广',
                             '销量', '低至', '返厂', '开奖', '抽奖', '公众号', '公主号', '多重好礼', '购物券', '购物金', '套劵', '封顶', '爆款', '享好价',
                             '微信商城', '定制', '微课堂', '月卡', '11.11']
                    assert_title = True
                    for i2 in guolv:
                        if title.find(i2) != -1:
                            assert_title = False
                            break
                    if assert_title == False:
                        self.logger.info({"mark": "该文章标题有营销词跳过",
                                          "title": title, "gongzhonghao": s})
                        continue
                    try:
                        self.driver.implicitly_wait(3)
                        yuanchuang = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                            (By.XPATH,
                             '//*[@id="biz_detail_history_art_list"]/div[%d]/div[2]/div[%d]/div[1]/div[1]/div/span[2]' % (
                                 j, i + 1)))).text
                        if yuanchuang == '原创':
                            self.logger.info({"mark": "该文章原创跳过",
                                              "title": title, "gongzhonghao": s})
                            continue
                    except:
                        pass
                    current_time = int(time.time())
                    if len(imgs_three) == 0:
                        img1, img2, img3 = "", "", ""
                    elif len(imgs_three) == 1:
                        img1 = imgs_three[0]
                        img2, img3 = "", ""
                    elif len(imgs_three) == 2:
                        img1 = imgs_three[0]
                        img2 = imgs_three[1]
                        img3 = ""
                    elif len(imgs_three) >= 3:
                        img1 = imgs_three[0]
                        img2 = imgs_three[1]
                        img3 = imgs_three[2]
                    else:
                        img1, img2, img3 = "", "", ""
                    jsons = {
                        "author": author,
                        "categery1": obj2.categery1,
                        "categery2": obj2.categery2,
                        "categery3": obj2.categery3,
                        "content": content,
                        "currentTime": current_time,
                        "description": description,
                        "image1": img1,
                        "image2": img2,
                        "image3": img3,
                        "imagecount": img_count,
                        "origin": origin,
                        "retrieving": "",
                        "timestamp": timeStamp,
                        "title": title,
                        "url": lianjie,
                        "weight": 0
                    }
                    send_to_kafka(jsons)
                    self.logger.info({"mark": "文章爬取成功", "msg": "第" + str(i + 1) + "篇文章爬取成功",
                                      "title": title, "gongzhonghao": s, "categery1": obj2.categery1})

                except Exception as e:
                    print("error",traceback.format_exc())
                    break

            self.logger.info({"mark": "该组已爬完", "msg": "", "gongzhonghao": s})

        else:
            pass
