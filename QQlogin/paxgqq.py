import base64
import random
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
from QQlogin.viry2 import tx_test
from QQlogin.interf_qq import QQLogin
# from viryimg import CrackSlider #第一种直接滑的方案
import requests
class Pa_Paxgqq():
    def __init__(self):
        User_Agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0"]
        options = webdriver.ChromeOptions()
        options.add_argument('User-Agent=' + random.choice(User_Agents))
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        options.add_argument('--disable-extensions')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.url = "https://xg.qq.com/"
        self.wait=WebDriverWait(self.driver, 10)
    def main(self):
        self.driver.delete_all_cookies()
        self.driver.get(self.url)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.top-menu-wrapper.index-menu.js_localize > div > div > div.top-bar-right > ul > li:nth-child(4) > a > span"))).click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.app-wrapper > div > div > div > div > div > div.login-wrapper.el-col.el-col-8 > div > div > div.sign-options > div.sign-options__middle.gap > i"))).click()
        xg=QQLogin()
        xg.main(self.driver)
        print(self.driver.get_cookies())
        #[{'domain': 'xg.qq.com', 'expiry': 1566980223.092908, 'httpOnly': False, 'name': 'XGTicket', 'path': '/', 'secure': False, 'value': 'N3V2aThIcU9tSjRyYkZzTm5HS1JOZlM4TEFvRWViRllBRUljVWpNUXlVV1Vaem0vYUo2RUdvSllFWkN2VWsyK2VFekpLa084NjYwa3JOUGllL3d6ZDlrTFBHLzRHaE03VHgvdkNsOFFkSll5b0k0M3BFdnZJM2l5a2k4andER2ZGUnJjbm9WMUh1NTFJam9DM3JscXdLSGVyUEppRitOekJ5aUhQRmc5UFl2ektaWXo2eWhaMzhVY2R5QnU0QXdubTlKamdNL2hrVkQ2YitXbWhqL1NHUT09'}, {'domain': 'xg.qq.com', 'expiry': 1566974812, 'httpOnly': False, 'name': 'ts_last', 'path': '/', 'secure': False, 'value': 'xg.qq.com/app/ctr_index/index'}, {'domain': 'qq.com', 'expiry': 2147483646.666376, 'httpOnly': False, 'name': 'ptcz', 'path': '/', 'secure': False, 'value': '89ba6fd8088d78e10c67501e5c6aa47b4937ab834cdf2d6305eb40fa21ee3aa8'}, {'domain': 'qq.com', 'expiry': 2147483646.666342, 'httpOnly': False, 'name': 'RK', 'path': '/', 'secure': False, 'value': 'Cc6N0JHNaW'}, {'domain': 'xg.qq.com', 'expiry': 1566976590, 'httpOnly': False, 'name': '_qddamta_800047484', 'path': '/', 'secure': False, 'value': '3-0'}, {'domain': 'xg.qq.com', 'expiry': 1598508990, 'httpOnly': False, 'name': '_qddaz', 'path': '/', 'secure': False, 'value': 'QD.gdtldl.n6yniv.jzuv9dg7'}, {'domain': 'qq.com', 'httpOnly': False, 'name': 'pgv_info', 'path': '/', 'secure': False, 'value': 'ssid=s9730226916'}, {'domain': 'qq.com', 'httpOnly': False, 'name': 'pgv_si', 'path': '/', 'secure': False, 'value': 's7306490880'}, {'domain': 'qq.com', 'expiry': 2147385600, 'httpOnly': False, 'name': 'pgv_pvid', 'path': '/', 'secure': False, 'value': '4000293588'}, {'domain': 'qq.com', 'httpOnly': False, 'name': 'ptisp', 'path': '/', 'secure': False, 'value': 'cnc'}, {'domain': 'xg.qq.com', 'httpOnly': False, 'name': '_qddab', 'path': '/', 'secure': False, 'value': '3-ysezhq.jzuv9dga'}, {'domain': 'xg.qq.com', 'expiry': 1566974791, 'httpOnly': False, 'name': '_qdda', 'path': '/', 'secure': False, 'value': '3-1.1'}, {'domain': 'xg.qq.com', 'expiry': 1630045012, 'httpOnly': False, 'name': 'ts_uid', 'path': '/', 'secure': False, 'value': '4944300904'}, {'domain': 'xg.qq.com', 'expiry': 1566976613.867715, 'httpOnly': False, 'name': 'm_check', 'path': '/', 'secure': False, 'value': '1759ef9c'}, {'domain': 'qq.com', 'expiry': 2147385600, 'httpOnly': False, 'name': 'pgv_pvi', 'path': '/', 'secure': False, 'value': '1361417216'}, {'domain': 'xg.qq.com', 'httpOnly': False, 'name': 'PHPSESSID', 'path': '/', 'secure': False, 'value': '0rrfpg60b2as2j1omu3644a8g0'}]
        headers={"Connection":"keep-alive","Accept":"application/json","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36","Sec-Fetch-Mode":"cors","Sec-Fetch-Site":"same-origin","Referer":"https://xg.qq.com/app/ctr_index/index","Accept-Encoding":"gzip, deflate, br","Accept-Language":"zh-CN,zh;q=0.9"}
        cookies = {}
        for i in self.driver.get_cookies():
            cookies.update({i["name"]: i["value"]})
        res=requests.get("https://xg.qq.com/xg/user/ctr_info/get",headers=headers,cookies=cookies)
        res={"code": 0,
         "data": {"email": "858662854@qq.com", "phone": "18667026638", "nickname": "\u8001\u6731\u5c0f\u53f7",
                  "companyName": "\u5c0f\u9e21\u5403\u5927\u7c73", "location": "1,12,2", "emailIsValid": 1,
                  "phoneIsValid": 1, "qqFullName": "\u8001\u6731\u5c0f\u53f7", "isBindingQQ": 1}}
        proxy = {"https": "http://112.85.168.73:9999", "http": "http://112.85.168.73:9999"}
        print(res)

if __name__ == '__main__':
    p=Pa_Paxgqq()
    p.main()