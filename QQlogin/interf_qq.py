import base64
import random
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image

from QQlogin.viry2 import tx_test

# from viryimg import CrackSlider #第一种直接滑的方案

class QQLogin():
    # def __init__(self,url):
    #     User_Agents = [
    #         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    #         "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0"]
    #     options = webdriver.ChromeOptions()
    #     options.add_argument('User-Agent=' + random.choice(User_Agents))
    #     options.add_experimental_option("excludeSwitches", ['enable-automation'])
    #     options.add_argument('--disable-extensions')
    #     driver = webdriver.Chrome(chrome_options=options)
    #     self.url = url

    def wait_for_one(self, elements,driver):
        time.sleep(1)
        for (key, value) in elements.items():
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, value)))
                # driver.find_element_by_css_selector(value)
                return key
            except Exception:
                continue

    # 异步多种等待
    def othermethod(self,driver):
        found = self.wait_for_one({
            "slide": "#ptlogin_iframe",
            "datapage": "#userInfoNickName",
            "fullpage": "#page > div > div:nth-child(2) > div > div > div > div.text.title"
        },driver=driver)

        if found == 'datapage':
            print('logined')
        elif found == 'fullpage':
            print('logined')
        elif found == 'slide':
            driver.switch_to.frame(driver.find_element_by_css_selector("#ptlogin_iframe"))
            ifr2 = driver.find_elements_by_css_selector("#tcaptcha_iframe")
            img = driver.find_elements_by_css_selector("#qlogin_tips_2")  # 由于你的帐号存在异常，需要进行手机验证，请使用QQ手机版扫码进行登录。
            if len(ifr2) == 0 and len(img):  # 扫码
                if img[0].get_attribute('style') == 'display: block;':
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                        (By.XPATH, "//*[@id='qlogin_tips_2' and contains(text(),'由于你的帐号存在异常，需要进行手机验证')]")))
                    time.sleep(1)
                    screenshot = driver.find_element_by_xpath("//*[@id='qrlogin_img']").screenshot_as_base64
                    print("screenshot", screenshot)

                    imgdata = base64.b64decode(screenshot)
                    print("imgdata", imgdata)
                    file = open('2.jpg', 'wb')
                    file.write(imgdata)
                    file.close()
                    im = Image.open('2.jpg')
                    im.show()
                    time.sleep(3)
                    try:
                        result = WebDriverWait(driver, 10).until(EC.alert_is_present())
                        result.accept()
                        loginbtn = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#loginBtn")))
                        if len(loginbtn):
                            loginbtn[0].click()
                    # css body > div.new - navbar > div > div.navbar - hd > div > h1 > a
                    except Exception as E:
                        print(E)
                elif img[0].get_attribute('style') == 'display: none;':
                    print("你输入的帐号或密码不正确，请重新输入000")
            elif len(ifr2):  #滑块
                driver.switch_to.default_content()
                driver.switch_to.frame(driver.find_element_by_css_selector("#ptlogin_iframe"))
                driver.switch_to.frame(driver.find_element_by_css_selector("#tcaptcha_iframe"))
                c = tx_test(url=driver.current_url, driver=driver)
                c.login()
            else:
                print("输入框输完后别的情况")
                if len(driver.find_elements_by_css_selector("#loginBtn")):
                    driver.find_elements_by_css_selector("#loginBtn")[0].click()
                print("登录成功1")
        else:
            print('登录成功2')

    # 主程序
    def open(self,driver,url):
        driver.get(url)
        driver.delete_all_cookies()
        driver.get(url)
        if driver.find_elements_by_css_selector("#userName")[0].get_attribute('textContent') == '你好':
            print("logined")
        else:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='loginBtn']")))
            element.click()
    def main(self,driver):
        driver.switch_to.default_content()
        driver.switch_to.frame(driver.find_element_by_id("ptlogin_iframe"))
        a = input("请输入登录方式编号 1(扫码)2(输入账号密码)：")
        if a == "1":  # 直接扫码
            screenshot = driver.find_element_by_xpath("//*[@id='qrlogin_img']").screenshot_as_base64
            # print("screenshot", screenshot)
            imgdata = base64.b64decode(screenshot)
            # print("imgdata", imgdata)
            file = open('1.jpg', 'wb')
            file.write(imgdata)
            file.close()

            im = Image.open('1.jpg')
            im.show()

            time.sleep(20)
            try:
                result = WebDriverWait(driver, 10).until(EC.alert_is_present())
                result.accept()
                loginbtn = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#loginBtn")))
                if len(loginbtn):
                    loginbtn[0].click()
            except Exception as E:
                print("无弹窗",E)
        elif a == "2":
            # 输入账号密码后的聚合方法
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#switcher_plogin")))
            element.click()

            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='u']")))
            element.clear()
            element.send_keys('398946147')

            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='p']")))
            element.send_keys('369zsx4218!')

            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='login_button']")))
            time.sleep(1)
            element.click()
            if not EC.alert_is_present()(driver):
                driver.switch_to.default_content()
                self.othermethod(driver=driver)
            else:
                try:
                    result = WebDriverWait(driver, 10).until(EC.alert_is_present())
                    result.accept()
                except Exception as E:
                    print(E)

                try:
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#loginBtn")))
                    element.click()
                finally:
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id='userInfoNickName']")))
                    if element.get_attribute('textContent') == '鹰凌香痕':
                        print("LoginSuccess")
        else:
            print("请重新输入")


if __name__ == '__main__':
    # qlogin = QQLogin()
    # qlogin.main()
    b=1
    a="asdfqewr%%mfwerqer%%c%s" %b
    print(a)
