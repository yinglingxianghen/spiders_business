# -*- coding: utf-8 -*-
import base64
import datetime
import json
import os
import random
import time
from io import BytesIO

import requests
import redis
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
from interactors import BaseSpider, SpiderInteractor
# from configs.logconfs.config import log
# from configs.logconfs.config_schedule import log_schedule
from models.task_info import TaskInfo
from models.ocean_models import *
from utils.save_to_txt import dump_all
from utils.get_proxy import GetProxies
proxy_ip_port="125.123.67.175:22978"
try:
    resu = GetProxies().test_proxy_letftime(proxy_ip_port)
    # print("resu",resu,type(resu))
    assert resu == True
except Exception as e:
    print("____________________________________________________________________")
    proxy = GetProxies().get(mode="loose")
    if isinstance(proxy, dict) and "code" in proxy and proxy["code"] == -2:
        proxy = GetProxies().get(mode="loose")
    proxy_ip_port = proxy.split(",")[0]
    print("a", GetProxies().test_proxy_letftime(proxy_ip_port))
    if not GetProxies().test_proxy_letftime(proxy_ip_port):
        print("if not GetProxies().test_proxy_letftime(proxy_ip_port):")
        proxy_ip_port = GetProxies().get_proxy_casual()
        print("proxy_ip_port", proxy_ip_port)
print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
from utils.verify_code import Chaojiying_Client
from configs.conf import conf
import pymysql

from spiders.download_ocean_mysql import data_into_db
from utils.excel_2_mysql import excel_to_mysql
from spider_manager import *

class OceanengineSpider(BaseSpider):
    def __init__(self,task_info,spider_context):
        super(OceanengineSpider,self).__init__(task_info,spider_context)
        self.task_name=task_info.task_name
        self.task_id=task_info.task_id
        self.info_id=task_info.info_id
        self.spider_name=task_info.spider_name
        self.last_proxy=task_info.last_proxy
        self.r = redis.Redis(host='localhost', port=6379,decode_responses=True)
        self.r1 = redis.Redis(host='localhost', port=6379,decode_responses=True,db=1)

        self.url="https://ad.oceanengine.com"

    def getcode(self):
        # self.spider_context.report()
        print("getcode")
        # self.r.publish('vrcode', json.dumps({'type': self.type, 'num': self.num}))
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
    def get_veryfy_code(self,driver):
        screenshot=WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,"//*[@id=\"login\"]/section/div[3]/div[6]/div"))).get_attribute("style")
        # screenshot = driver.find_element_by_xpath("//*[@id=\"login\"]/section/div[3]/div[6]/div").get_attribute("style")
        b6 = re.search(r'gif;base64,(.*?)\"\);', screenshot).group(1)
        print("screenshot", screenshot,type(screenshot))
        # screenshot = Image.open(BytesIO(screenshot))
        # screenshot.show()

        bytesdata = base64.b64decode(b6)
        screenshot = Image.open(BytesIO(bytesdata))
        screenshot.save(os.path.dirname(__file__)+r'../../media/imags/code.png', 'png')
        # screenshot.show()
        chaojiying = Chaojiying_Client('yinglingno1', '369zsx4218', '901548')  # 用户中心>>软件ID 生成一个替换 96001

        im = open(os.path.dirname(__file__)+r'../../media/imags/code.png', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
        print(chaojiying.PostPic(im, 1902)["pic_str"])
        return chaojiying.PostPic(im, 1902)["pic_str"] # 1902 验证码类型  官方网站>>价格体系 3.4+版 print 后要加()

    def obtain_task_info(self):
        print(self.task_info().spider_name)
    current_dir=os.path.dirname(__file__)
    def start_requests(self):    #登录
        log_schedule.warning("巨量引擎爬取开始")
        User_Agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0"]
        # url = "https://ad.oceanengine.com"
        options = webdriver.ChromeOptions()
        options.add_argument('User-Agent=' + random.choice(User_Agents))
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('window-size=1920x1480')
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(self.url)
        self.driver.maximize_window()
        log.warning(self.driver.title)

        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='login']/section/div[3]/div[4]/input"))).send_keys(conf['ocean_account']["username"])
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='login']/section/div[3]/div[5]/input[1]"))).send_keys(conf['ocean_account']["pwd"])

        #method2
        # WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='login']/section/div[3]/div[5]/input[2]/"))).send_keys("adafswer")
        # self.driver.execute_script('document.evaluate("//*[@id=\'login\']/section/div[3]/div[5]/input[1]",document).iterateNext().remove()')

        b=input("请输入验证码:")

        # b=self.spider_context().wait_for_verify_code()
        # b=self.getcode()
        # b = self.get_veryfy_code(self.driver)
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='login']/section/div[3]/div[6]/input"))).send_keys(b)
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='login']/section/div[3]/div[10]/div"))).click()

        cookies=self.driver.get_cookies()
        dicts={i["name"]:i["value"] for i in cookies}
        print("dicts",dicts)
        proxy_ip_port=self.last_proxy
        print("proxy_IP_port",proxy_ip_port)
        try:
            res = requests.get("https://www.baidu.com",proxies={"http": "http://%s"%proxy_ip_port, "https": "https://%s"%proxy_ip_port},timeout=3)
            assert res.status_code==200
        except:
            proxy=GetProxies().get(mode="loose")
            if  isinstance(proxy,dict) and "code" in proxy and proxy["code"]==-2:
                proxy=GetProxies().get(mode="loose")
            proxy_ip_port=proxy.split(",")[0]
        self.r1.set(self.spider_name,proxy_ip_port)

        # "X-OverrideGateway": proxy_ip_port,
        # proxy_ip_port="49.67.147.115:15128"
        # "Referer": "https://ad.oceanengine.com/pages/login/index.html",
        headers={"X-OverrideGateway": proxy_ip_port,"Connection":"keep-alive","Sec-Fetch-Mode":"cors","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3","Sec-Fetch-Site":"same-origin","Accept-Encoding":"gzip,deflate, br","Accept-Language":"zh-CN,zh;q=0.9"}

        n=0
        session = requests.session()
        # session.cookies.clear()
        # session.proxies = {"http":"http://127.0.0.1:8888", "https":"http://127.0.0.1:8888"}
        session.cookies = requests.utils.cookiejar_from_dict(dicts, cookiejar=None, overwrite=True)

        # 首页图表数据
        res=session.get("https://ad.oceanengine.com/overture/index/advertiser_chart/?st=2019-08-22&et=2019-08-28&_=1567064637411",headers=headers,verify=False)
        log.warning("#首页图表数据",res.text)
        # dump_all(res, n=n)
        n+=1
        print("a",json.loads(res.text)["data"])
        SpiderManager().send_result("爬虫结束")

        # 4.2.1 推广-创意
        url = "https://ad.oceanengine.com/statistics/data_v2/creative_stat/?page=1&limit=20&st=2019-08-29&et=2019-08-29&status=&landing_type=0&image_mode=0&creative_material_mode=2&pricing=0&search_type=3&keyword=&sort_stat=&sort_order=0&smart_bid_type=&_=1567066541153"
        res421 = session.get(url)
        dump_all(res421, n=n)
        n += 1
        log.warning("推广-创意", res421.text)
        # msg='res421.text'
        # print(type(res421.text),"推广创意")
        # sql="insert into sprea_idea (msgs) value ('{\"status\": \"success\", \"data\": {\"table\": {\"pagination\": {\"has_more\": false, \"total_count\": 0, \"page_count\": 0, \"limit\": 20, \"display_pagination_count\": 5, \"offset\": 0, \"base_query\": {}, \"page\": 1, \"use_offset\": false}, \"statistics\": {\"form_submit\": 0, \"show\": 0, \"active_show\": 0, \"click_call_cost\": \"0.00\", \"next_day_open_rate\": \"0.00\", \"pre_interactive_cost\": 0, \"follow\": 0, \"active_register_click_cost\": \"0.00\", \"home_visited\": 0, \"redirect\": 0, \"valid_play\": 0, \"click_start\": 0, \"game_active_rate\": \"0.00\", \"in_app_uv\": 0, \"share_count\": 0, \"active_register_cost\": \"0.00\", \"active_pay_click\": 0, \"click_website\": 0, \"total_play\": 0, \"dy_interaction\": 0, \"active_register_rate\": \"0.00\", \"click_start_rate\": \"0.00\", \"active_click\": 0, \"mtt_click\": 0, \"convert_cnt\": 0, \"qq\": 0, \"multi_native_action\": 0, \"activate_cost\": \"0.00\", \"like\": 0, \"repin_count\": 0, \"click_cnt\": 0, \"button\": 0, \"click_cost\": \"0.00\", \"in_app_cart\": 0, \"ctr_higher_of_inventory\": \"0.00\", \"activate_rate\": \"0.00\", \"active_cost\": \"0.00\", \"active_register_show\": 0, \"next_day_open\": 0, \"view\": 0, \"game_pay_rate\": \"0.00\", \"game_addiction\": 0, \"convert_cost\": \"0.00\", \"active_rate\": \"0.00\", \"active_pay_show_cost\": \"0.00\", \"active_pay_cost\": \"0.00\", \"vote\": 0, \"active_pay_show\": 0, \"click\": 0, \"click_start_cnt\": 0, \"install_finish_rate\": \"0.00\", \"valid_play_rate\": \"0.00\", \"active_register_click\": 0, \"conversion_cost\": \"0.00\", \"click_call_cnt\": 0, \"coupon_addition\": 0, \"redirect_to_shop\": 0, \"install_finish_cost\": \"0.00\", \"customer_effective\": 0, \"play_duration_sum\": \"0.00\", \"download_start\": 0, \"ies_challenge_click\": 0, \"click_start_cost\": \"0.00\", \"click_call\": 0, \"show_cnt\": 0, \"customer_effective_rate\": \"0.00\", \"convert\": 0, \"ctr\": \"0.00\", \"game_pay_cost\": \"0.00\", \"positive_play\": 0, \"wechat\": 0, \"install_finish\": 0, \"consult_effective\": 0, \"coupon\": 0, \"convert_rate\": \"0.00\", \"coverage_show\": \"0.00\", \"click_landing_page\": 0, \"game_pay\": 0, \"active_pay_avg_amount\": \"0.00\", \"game_active_cost\": \"0.00\", \"conversion_rate\": \"0.00\", \"activate\": 0, \"ecpm\": \"0.00\", \"download_finish_cost\": 0, \"message_action\": 0, \"message\": 0, \"poi_multiple\": 0, \"poi_collect\": 0, \"active_register_show_cost\": \"0.00\", \"lottery\": 0, \"active_click_cost\": \"0.00\", \"click_call_rate\": \"0.00\", \"comment_count\": 0, \"download_finish_rate\": \"0.00\", \"xpath\": 0, \"phone_connect\": 0, \"game_addiction_cost\": \"0.00\", \"shopping\": 0, \"form\": 0, \"customer_effective_cost\": \"0.00\", \"effective_play_rate\": \"0.00\", \"phone\": 0, \"consult\": 0, \"game_addiction_rate\": \"0.00\", \"active_pay_rate\": \"0.00\", \"effective_play\": 0, \"poi_address_click\": 0, \"map_search\": 0, \"coverage_cost\": \"0.00\", \"in_app_order\": 0, \"click_call_dy\": 0, \"click_download\": 0, \"ctr_higher_of_industry\": \"0.00\", \"form_click_button\": 0, \"active_pay_amount\": \"0.00\", \"install_finish_cnt\": 0, \"detail_stat\": [], \"ies_music_click\": 0, \"coupon_single_page\": 0, \"valid_play_cost\": \"0.00\", \"download_finish\": 0, \"stat_cost\": \"0.00\", \"active_pay_click_cost\": \"0.00\", \"download_finish_cnt\": 0, \"phone_effective\": 0, \"in_app_detail_uv\": 0, \"click_counsel\": 0, \"phone_confirm\": 0, \"game_active\": 0, \"reservation\": 0, \"average_video_play\": \"0.00\", \"click_shopwindow\": 0, \"cpm\": \"0.00\", \"active_show_cost\": \"0.00\", \"cpc\": \"0.00\", \"in_app_pay\": 0, \"download_cost\": \"0.00\", \"next_day_open_cost\": \"0.00\", \"effective_play_cost\": \"0.00\"}, \"creative_data\": []}, \"chart\": {}}}')"
        sql = "insert into sprea_idea (msgs) value ('%s')" % res421.text
        # data_into_db(sql)

        # 4221报表-广告报表-账户报表-分日-选择今日-详细数据
        url = "https://ad.oceanengine.com/statistics/promote/advertiser_stat/"
        data = {"st": "2019-09-09", "et": "2019-09-15", "day": 1, "page": 1, "limit": 20, "sort_stat": "stat_time_day",
                "sort_order": 0, "dims": "advertiser_id",
                "fields": ["show_cnt", "click_cnt", "ctr", "cpc_platform", "cpm_platform", "stat_cost", "convert_cnt",
                           "conversion_cost", "conversion_rate", "deep_convert_cnt", "deep_convert_cost",
                           "deep_convert_rate"]}

        xcsrft = session.cookies.get_dict()["csrftoken"]
        print("xcsrft1",xcsrft,dict(session.cookies))
        headers = {"Connection": "keep-alive", "Content-Length": "322", "Pragma": "no-cache",
                   "Cache-Control": "no-cache", "Accept": "application/json,text/javascript,*/*;q=0.01",
                   "X-CSRFToken": xcsrft, "X-Requested-With": "XMLHttpRequest",
                   "User-Agent": "Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
                   "Sec-Fetch-Mode": "cors", "Content-Type": "application/json", "Origin": "https://ad.oceanengine.com",
                   "Sec-Fetch-Site": "same-origin",
                   "Referer": "https://ad.oceanengine.com/pages/reporter/ad-report.html?report_type=advertiser",
                   "Accept-Encoding": "gzip,deflate,br", "Accept-Language": "zh-CN,zh;q=0.9"}
        res4221 = session.post(url, data=json.dumps(data), headers=headers)
        log.warning(res4221.text)
        dump_all(res4221, n=n)
        n += 1

        # 4.2.0 推广-广告组
        url = "https://ad.oceanengine.com/promote/campaign/stat_list/"
        data2={"st":"2019-09-23","et":"2019-09-23","page":1,"limit":100,"fields":["stat_cost","show_cnt","cpm_platform","click_cnt","cpc_platform","ctr","convert_cnt","conversion_cost","conversion_rate","dy_share","dy_like","dy_follow","dy_home_visited","ies_challenge_click","ies_music_click","location_click","dy_comment","total_play","valid_play","valid_play_rate","valid_play_cost","play_25_feed_break","play_50_feed_break","play_75_feed_break","play_99_feed_break","play_over_rate","average_play_time_per_play","wifi_play_rate","click_call_cnt","click_counsel","form_click_button","coupon_addition","phone","form","map","button","view","download_start","qq","lottery","vote","message","redirect","shopping","consult","wechat","phone_confirm","phone_connect","consult_effective","coupon","coupon_single_page","click_start_cnt","click_start_cost","click_start_rate","download_finish_cnt","download_finish_cost","download_finish_rate","install_finish_cnt","install_finish_cost","install_finish_rate","active","active_cost","active_rate","active_register","active_register_cost","active_register_rate","game_addiction","game_addiction_cost","game_addiction_rate","attribution_next_day_open_cnt","attribution_next_day_open_cost","attribution_next_day_open_rate","next_day_open","active_pay","active_pay_cost","active_pay_rate","in_app_uv","in_app_detail_uv","in_app_cart","in_app_order","in_app_pay","loan_completion","loan_completion_cost","loan_completion_rate","pre_loan_credit","pre_loan_credit_cost","loan_credit","loan_credit_cost","loan_credit_rate","attribution_convert_cnt","attribution_convert_cost","attribution_deep_convert_cnt","attribution_deep_convert_cost"],"sort_stat":"create_time","sort_order":1,"campaign_status":[1]}
        headers2 = {"Connection": "keep-alive", "Content-Length": "322", "Pragma": "no-cache",
                   "Cache-Control": "no-cache", "Accept": "application/json,text/javascript,*/*;q=0.01",
                   "X-CSRFToken": xcsrft, "X-Requested-With": "XMLHttpRequest",
                   "User-Agent": "Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
                   "Sec-Fetch-Mode": "cors", "Content-Type": "application/json", "Origin": "https://ad.oceanengine.com",
                   "Sec-Fetch-Site": "same-origin",
                   "Referer": "https://ad.oceanengine.com/pages/promotion.html",
                   "Accept-Encoding": "gzip,deflate,br", "Accept-Language": "zh-CN,zh;q=0.9"}
        xcsrft2 = session.cookies.get_dict()["csrftoken"]
        print("xcsrft2", xcsrft2,dict(session.cookies))
        res420 = session.post(url,data=json.dumps(data2), headers=headers2)
        dump_all(res420, n=n)
        n += 1
        log.warning("推广-广告组",res420.text)
        print(res420.text,type(res420.text))
        # msg='res421.text'
        # print(type(res421.text),"推广创意")
        # sql="insert into sprea_idea (msgs) value ('{\"status\": \"success\", \"data\": {\"table\": {\"pagination\": {\"has_more\": false, \"total_count\": 0, \"page_count\": 0, \"limit\": 20, \"display_pagination_count\": 5, \"offset\": 0, \"base_query\": {}, \"page\": 1, \"use_offset\": false}, \"statistics\": {\"form_submit\": 0, \"show\": 0, \"active_show\": 0, \"click_call_cost\": \"0.00\", \"next_day_open_rate\": \"0.00\", \"pre_interactive_cost\": 0, \"follow\": 0, \"active_register_click_cost\": \"0.00\", \"home_visited\": 0, \"redirect\": 0, \"valid_play\": 0, \"click_start\": 0, \"game_active_rate\": \"0.00\", \"in_app_uv\": 0, \"share_count\": 0, \"active_register_cost\": \"0.00\", \"active_pay_click\": 0, \"click_website\": 0, \"total_play\": 0, \"dy_interaction\": 0, \"active_register_rate\": \"0.00\", \"click_start_rate\": \"0.00\", \"active_click\": 0, \"mtt_click\": 0, \"convert_cnt\": 0, \"qq\": 0, \"multi_native_action\": 0, \"activate_cost\": \"0.00\", \"like\": 0, \"repin_count\": 0, \"click_cnt\": 0, \"button\": 0, \"click_cost\": \"0.00\", \"in_app_cart\": 0, \"ctr_higher_of_inventory\": \"0.00\", \"activate_rate\": \"0.00\", \"active_cost\": \"0.00\", \"active_register_show\": 0, \"next_day_open\": 0, \"view\": 0, \"game_pay_rate\": \"0.00\", \"game_addiction\": 0, \"convert_cost\": \"0.00\", \"active_rate\": \"0.00\", \"active_pay_show_cost\": \"0.00\", \"active_pay_cost\": \"0.00\", \"vote\": 0, \"active_pay_show\": 0, \"click\": 0, \"click_start_cnt\": 0, \"install_finish_rate\": \"0.00\", \"valid_play_rate\": \"0.00\", \"active_register_click\": 0, \"conversion_cost\": \"0.00\", \"click_call_cnt\": 0, \"coupon_addition\": 0, \"redirect_to_shop\": 0, \"install_finish_cost\": \"0.00\", \"customer_effective\": 0, \"play_duration_sum\": \"0.00\", \"download_start\": 0, \"ies_challenge_click\": 0, \"click_start_cost\": \"0.00\", \"click_call\": 0, \"show_cnt\": 0, \"customer_effective_rate\": \"0.00\", \"convert\": 0, \"ctr\": \"0.00\", \"game_pay_cost\": \"0.00\", \"positive_play\": 0, \"wechat\": 0, \"install_finish\": 0, \"consult_effective\": 0, \"coupon\": 0, \"convert_rate\": \"0.00\", \"coverage_show\": \"0.00\", \"click_landing_page\": 0, \"game_pay\": 0, \"active_pay_avg_amount\": \"0.00\", \"game_active_cost\": \"0.00\", \"conversion_rate\": \"0.00\", \"activate\": 0, \"ecpm\": \"0.00\", \"download_finish_cost\": 0, \"message_action\": 0, \"message\": 0, \"poi_multiple\": 0, \"poi_collect\": 0, \"active_register_show_cost\": \"0.00\", \"lottery\": 0, \"active_click_cost\": \"0.00\", \"click_call_rate\": \"0.00\", \"comment_count\": 0, \"download_finish_rate\": \"0.00\", \"xpath\": 0, \"phone_connect\": 0, \"game_addiction_cost\": \"0.00\", \"shopping\": 0, \"form\": 0, \"customer_effective_cost\": \"0.00\", \"effective_play_rate\": \"0.00\", \"phone\": 0, \"consult\": 0, \"game_addiction_rate\": \"0.00\", \"active_pay_rate\": \"0.00\", \"effective_play\": 0, \"poi_address_click\": 0, \"map_search\": 0, \"coverage_cost\": \"0.00\", \"in_app_order\": 0, \"click_call_dy\": 0, \"click_download\": 0, \"ctr_higher_of_industry\": \"0.00\", \"form_click_button\": 0, \"active_pay_amount\": \"0.00\", \"install_finish_cnt\": 0, \"detail_stat\": [], \"ies_music_click\": 0, \"coupon_single_page\": 0, \"valid_play_cost\": \"0.00\", \"download_finish\": 0, \"stat_cost\": \"0.00\", \"active_pay_click_cost\": \"0.00\", \"download_finish_cnt\": 0, \"phone_effective\": 0, \"in_app_detail_uv\": 0, \"click_counsel\": 0, \"phone_confirm\": 0, \"game_active\": 0, \"reservation\": 0, \"average_video_play\": \"0.00\", \"click_shopwindow\": 0, \"cpm\": \"0.00\", \"active_show_cost\": \"0.00\", \"cpc\": \"0.00\", \"in_app_pay\": 0, \"download_cost\": \"0.00\", \"next_day_open_cost\": \"0.00\", \"effective_play_cost\": \"0.00\"}, \"creative_data\": []}, \"chart\": {}}}')"
        sql="insert into sprea_idea (msgs) value ('%s')" %res420.text
        # data_into_db(sql)

        # for i in json.loads(res420.text)["data"]["campaigns"]:
        #     print(i["budget"],i["campaign_name"],i["campaign_status"],i["landing_type_name"],i["stat_data"]["show_cnt"],i["stat_data"]["click_cnt"],i["stat_data"]["stat_cost"],
        #           i["stat_data"]["convert_cnt"],i["stat_data"]["cpc_platform"],i["stat_data"]["cpm_platform"],i["stat_data"]["conversion_cost"],i["stat_data"]["conversion_rate"],
        #           i["stat_data"]["click_start_rate"])
        #     o=Ocean_Test_Adgs(budget=i["budget"],campaign_name=i["campaign_name"],campaign_status=i["campaign_status"],landing_type_name=i["landing_type_name"],show_cnt=i["stat_data"]["show_cnt"],click_cnt=i["stat_data"]["click_cnt"],stat_cost=i["stat_data"]["stat_cost"],
        #                       convert_cnt= i["stat_data"]["convert_cnt"],cpc_platform=i["stat_data"]["cpc_platform"],cpm_platform=i["stat_data"]["cpm_platform"],conversion_cost=i["stat_data"]["conversion_cost"],conversion_rate=i["stat_data"]["conversion_rate"],click_start_rate=i["stat_data"]["click_start_rate"])
        #     DBSession = sessionmaker(bind=engine)
        #     s = DBSession()
        #     s.add(o)
        #     s.commit()
        #     print("哦了")
        #     time.sleep(0.5)
        # 4222报表-广告报表-广告组报表-分日-选择今日-详细数据
        url="https://ad.oceanengine.com/statistics/promote/campaign_stat/"
        data={"st":"2019-08-23","et":"2019-08-29","day":1,"page":1,"limit":20,"sort_stat":"stat_time_day","sort_order":0,"dims":"advertiser_id","fields":["show_cnt","click_cnt","ctr","cpc_platform","cpm_platform","stat_cost","convert_cnt","conversion_cost","conversion_rate","deep_convert_cnt","deep_convert_cost","deep_convert_rate"]}
        res4222=session.post(url,data=json.dumps(data),headers=headers)

        log.warning(res4222.text)
        dump_all(res4222,n=n)
        n+=1

        # 4223报表-广告报表-广告计划报表-分日-选择今日-详细数据
        url="https://ad.oceanengine.com/statistics/promote/ad_stat/"
        data={"st":"2019-08-23","et":"2019-08-29","day":1,"page":1,"limit":20,"sort_stat":"stat_time_day","sort_order":0,"dims":"ad_id","fields":["show_cnt","click_cnt","ctr","cpc_platform","cpm_platform","stat_cost","convert_cnt","conversion_cost","conversion_rate","deep_convert_cnt","deep_convert_cost","deep_convert_rate"]}
        res4223=session.post(url,data=json.dumps(data),headers=headers)
        log.warning(res4223.text)
        dump_all(res4223,n=n)
        n+=1

        # 4224报表-广告报表-广告创意报表-分日-选择今日-详细数据
        url="https://ad.oceanengine.com/statistics/promote/creative_stat/"
        data={"st":"2019-08-23","et":"2019-08-29","day":1,"page":1,"limit":20,"sort_stat":"stat_time_day","sort_order":0,"dims":"ad_id","fields":["show_cnt","click_cnt","ctr","cpc_platform","cpm_platform","stat_cost","convert_cnt","conversion_cost","conversion_rate","deep_convert_cnt","deep_convert_cost","deep_convert_rate"]}
        res4224=session.post(url,data=json.dumps(data),headers=headers)
        log.warning(res4224.text)
        dump_all(res4224,n=n)
        n+=1

        # 4231报表-广告报表-账户报表-分日-选择昨日-详细数据
        url="https://ad.oceanengine.com/statistics/promote/advertiser_stat/"
        data={"st":"2019-08-28","et":"2019-08-28","day":1,"page":1,"limit":20,"sort_stat":"stat_time_day","sort_order":0,"dims":"ad_id","fields":["show_cnt","click_cnt","ctr","cpc_platform","cpm_platform","stat_cost","convert_cnt","conversion_cost","conversion_rate","deep_convert_cnt","deep_convert_cost","deep_convert_rate"]}
        data2={"st": "2019-10-01", "et": "2019-10-07", "day": 1, "page": 1, "sort_stat": "stat_time_day", "sort_order": 0,
         "dims": "advertiser_id", "compare": 0, "action": "download", "version": 1,
         "fields": ["show_cnt", "click_cnt", "ctr", "cpc_platform", "cpm_platform", "stat_cost", "convert_cnt",
                    "conversion_cost", "conversion_rate", "deep_convert_cnt", "deep_convert_cost", "deep_convert_rate"],
         "query_list": "stat_time_day,show_cnt,click_cnt,ctr,cpc_platform,cpm_platform,stat_cost,convert_cnt,conversion_cost,conversion_rate,deep_convert_cnt,deep_convert_cost,deep_convert_rate"}

        res4231=session.post(url,data=json.dumps(data),headers=headers)
        log.warning(res4231.text)
        dump_all(res4231,n=n)
        n+=1

        res42301=session.post(url,data=json.dumps(data2),headers=headers)
        download_id = json.loads(res42301.text)['data']['download_id']
        print('download_id', download_id,type(download_id))

        # 42300000000报表-广告报表-账户报表-下载表
        headers3 = {"Connection": "keep-alive", "Pragma": "no-cache",
                   "Cache-Control": "no-cache", "Accept": "application/json,text/javascript,*/*;q=0.01",
                   "X-Requested-With": "XMLHttpRequest",
                   "Content-type":"application/x-www-form-urlencoded",
                   "User-Agent": "Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
                   "Sec-Fetch-Mode": "cors",
                   "Sec-Fetch-Site": "same-origin",
                   "Referer":"https://ad.oceanengine.com/pages/reporter/ad-report.html?report_type=advertiser",
                   "Accept-Encoding": "gzip,deflate,br", "Accept-Language": "zh-CN,zh;q=0.9"}
        url="https://ad.oceanengine.com/statistics/data/download_stat/?st=2019-10-01&et=2019-10-07&day=1&page=1&sort_stat=stat_time_day&sort_order=0&dims=advertiser_id&compare=0&action=download&version=1&fields=show_cnt%2Cclick_cnt%2Cctr%2Ccpc_platform%2Ccpm_platform%2Cstat_cost%2Cconvert_cnt%2Cconversion_cost%2Cconversion_rate%2Cdeep_convert_cnt%2Cdeep_convert_cost%2Cdeep_convert_rate&query_list=stat_time_day%2Cshow_cnt%2Cclick_cnt%2Cctr%2Ccpc_platform%2Ccpm_platform%2Cstat_cost%2Cconvert_cnt%2Cconversion_cost%2Cconversion_rate%2Cdeep_convert_cnt%2Cdeep_convert_cost%2Cdeep_convert_rate&download_id="+download_id
        print("url",url)
        time.sleep(1)
        res4230=session.get(url,headers=headers3,verify=False)
        print("res4230.text",res4230.text)

        with open("down_excel.xls",'wb') as f:
            f.write(res4230.content)
        excel_to_mysql("down_excel.xls","test_report_account_realtime")

        # res42300 = session.get(url, headers=headers3, verify=False)
        # print("res42300.text", res42300.text)

        # 4232 报表-广告报表-广告组报表-分日-选择昨日-详细数据
        url="https://ad.oceanengine.com/statistics/promote/campaign_stat/"
        data={"st":"2019-08-28","et":"2019-08-28","day":1,"page":1,"limit":20,"sort_stat":"stat_time_day","sort_order":0,"dims":"campaign_id","fields":["show_cnt","click_cnt","ctr","cpc_platform","cpm_platform","stat_cost","convert_cnt","conversion_cost","conversion_rate","deep_convert_cnt","deep_convert_cost","deep_convert_rate"]}
        res4232=session.post(url,data=json.dumps(data),headers=headers,verify=False)
        log.warning(res4232.text)
        dump_all(res4232,n=n)
        n+=10

        # 4233报表-广告报表-广告计划报表-分日-选择昨日-详细数据
        url="https://ad.oceanengine.com/statistics/promote/ad_stat/"
        data={"st":"2019-08-28","et":"2019-08-28","day":1,"page":1,"limit":20,"sort_stat":"stat_time_day","sort_order":0,"dims":"campaign_id","fields":["show_cnt","click_cnt","ctr","cpc_platform","cpm_platform","stat_cost","convert_cnt","conversion_cost","conversion_rate","deep_convert_cnt","deep_convert_cost","deep_convert_rate"]}
        res4233=session.post(url,data=json.dumps(data),headers=headers,verify=False)
        log.warning(res4233.text)
        dump_all(res4233,n=n)
        n+=1

        # 4234报表-广告报表-广告创意报表-分日-选择昨日-详细数据
        url="https://ad.oceanengine.com/statistics/promote/creative_stat/"
        data={"st":"2019-08-28","et":"2019-08-28","day":1,"page":1,"limit":20,"sort_stat":"stat_time_day","sort_order":0,"dims":"campaign_id","fields":["show_cnt","click_cnt","ctr","cpc_platform","cpm_platform","stat_cost","convert_cnt","conversion_cost","conversion_rate","deep_convert_cnt","deep_convert_cost","deep_convert_rate"]}
        res4234=session.post(url,data=json.dumps(data),headers=headers)
        log.warning(res4234.text)
        dump_all(res4234,n=n)
        n+=1

        url="https://ad.oceanengine.com/statistics/audience/advertiser_table/"
        data={"st":"2019-08-28","et":"2019-08-28","day":1,"page":1,"limit":20,"sort_stat":"stat_time_day","sort_order":0,"dims":"campaign_id","fields":["show_cnt","click_cnt","ctr","cpc_platform","cpm_platform","stat_cost","convert_cnt","conversion_cost","conversion_rate","deep_convert_cnt","deep_convert_cost","deep_convert_rate"]}
        res4235=session.post(url,data=json.dumps(data),headers=headers)
        log.warning(res4235.text)
        dump_all(res4235,n=n)
        n+=1

        # 4235报表-受众分析-账户受众-选择昨日-详细数据-选择省份
        url="https://ad.oceanengine.com/statistics/audience/advertiser_chart/"
        data={"st":"2019-08-23","et":"2019-08-29","page":1,"dims":"province_name"}
        res4236=session.post(url,data=json.dumps(data),headers=headers)
        log.warning(res4236.text)
        dump_all(res4236,n=n)
        n+=1

        # 报表-受众分析-账户受众-选择昨日-详细数据-选择城市
        url="https://ad.oceanengine.com/statistics/audience/advertiser_chart/"
        data={"st":"2019-08-23","et":"2019-08-29","page":1,"dims":"city_name,province_name"}
        res4237=session.post(url,data=json.dumps(data),headers=headers)
        log.warning(res4237.text)
        dump_all(res4237,n=n)
        n+=1

        # 报表-受众分析-账户受众-选择昨日-详细数据-选择性别
        url="https://ad.oceanengine.com/statistics/audience/advertiser_chart/"
        data={"st":"2019-08-23","et":"2019-08-29","page":1,"dims":"gender"}
        res4238=session.post(url,data=json.dumps(data),headers=headers)
        log.warning(res4238.text)
        dump_all(res4238,n=n)
        n+=1

        # 报表-受众分析-账户受众-选择昨日-详细数据-选择年龄
        url="https://ad.oceanengine.com/statistics/audience/advertiser_chart/"
        data={"st":"2019-08-23","et":"2019-08-29","page":1,"dims":"age"}
        res4239=session.post(url,data=json.dumps(data),headers=headers)
        log.warning(res4239.text)
        dump_all(res4239,n=n)
        n+=1

        # 报表-受众分析-账户受众-选择昨日-详细数据-选择平台
        url="https://ad.oceanengine.com/statistics/audience/advertiser_chart/"
        data={"st":"2019-08-23","et":"2019-08-29","page":1,"dims":"platform"}
        res4240=session.post(url,data=json.dumps(data),headers=headers)
        log.warning(res4240.text)
        dump_all(res4240,n=n)
        n+=1

        # 报表-受众分析-账户受众-选择昨日-详细数据-选择兴趣标签
        url="https://ad.oceanengine.com/statistics/audience/advertiser_chart/"
        data={"st":"2019-08-23","et":"2019-08-29","page":1,"dims":"ad_tag"}
        res4241=session.post(url,data=json.dumps(data),headers=headers)
        log.warning(res4241.text)
        dump_all(res4241,n=n)
        n+=1

        # 报表-受众分析-账户受众-选择昨日-详细数据-选择兴趣关键词
        url="https://ad.oceanengine.com/statistics/audience/advertiser_chart/"
        data={"st":"2019-08-23","et":"2019-08-29","page":1,"dims":"ac"}
        res4242=session.post(url,data=json.dumps(data),headers=headers)
        log.warning(res4242.text)
        dump_all(res4242,n=n)
        n+=1
        # 账户-账号流水
        t = str(int(time.time() * 1000))
        url = "https://ad.oceanengine.com/overture/cash/get_cash_flow/?page=1&start_date=2019-01-01&end_date=2019-08-30&_=" + t
        log.warning(url)
        data = {"st": "2019-08-23", "et": "2019-08-29", "page": 1, "dims": "ac"}
        xcsrft1 = session.cookies.get_dict()["csrftoken"]
        headers1 = {"Connection": "keep-alive", "Origin": "https://ad.oceanengine.com", "Pragma": "no-cache",
                    "Cache-Control": "no-cache", "Accept": "application/json,text/javascript,*/*;q=0.01",
                    "X-CSRFToken": xcsrft1, "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": "Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
                    "Sec-Fetch-Mode": "cors", "Content-Type": "application/json", "Sec-Fetch-Site": "same-origin",
                    "Referer": "https://ad.oceanengine.com/overture/cash/flow/", "Accept-Encoding": "gzip,deflate,br",
                    "Accept-Language": "zh-CN,zh;q=0.9"}
        res4243 = session.get(url, headers=headers1)
        print("res4243.text", res4243.text)
        dump_all(res4243, n=n)
        n += 1

        log_schedule.warning("巨量引擎爬取正常结束")

# if __name__ == '__main__':
    # process = scrapy.crawler.CrawlerProcess()
    # d=process.crawl(OceanengineSpider,task_info=json.loads('{"taskid":1,"infoid":1,"task_name":"second"}', object_hook=dict2task),spider_context=SpiderInteractor())
    # OceanengineSpider().start_requests()
    # OceanengineSpider(task_info=TaskInfo(task_id=1, info_id=2, task_name="task_name",spider_name="spider_name",last_proxy="222.184.184.133:20529"),spider_context=SpiderInteractor()).start_requests()
