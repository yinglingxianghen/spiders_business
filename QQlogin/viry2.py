#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/4/1 11:12
# @File    : tx_test.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import requests
import random
import time
from QQlogin.get_distanct import *
class tx_test(object):
    def __init__(self,driver,url):
        self.driver = driver
        # self.driver.maximize_window()
        # 设置一个智能等待
        self.wait = WebDriverWait(self.driver, 2)
        self.url = url
    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        print(distance)
        distance += 20
        v = 0
        t = 0.2
        forward_tracks = []
        current = 0
        mid = distance * 3 / 5
        while current < distance:
            if current < mid:
                a = 20
            else:
                a = -10
            s = v * t + 0.5 * a * (t ** 2)
            v = v + a * t
            current += s
            forward_tracks.append(round(s))

        # back_tracks = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -1]
        back_tracks = [-3, -2, -1]
        # return {'forward_tracks': forward_tracks, 'back_tracks': back_tracks}
        return forward_tracks
        # 移动轨迹
        # track = []
        # # 当前位移
        # current = 0
        # # 减速阈值
        # mid = distance * 4 / 5
        # # 计算间隔
        # t = 0.2
        # # 初速度
        # v = 0.1
        # r = [1.1, 1.2, 1.3, 1.4, 1.5]
        # p = [2, 2.5, 2.8, 3, 3.5, 3.6]
        # q = 5.0
        # i = 0
        # while current < distance:
        #     if current < mid:
        #         # 加速度为正2
        #         a = 2
        #         q = q * 0.9
        #     else:
        #         # 加速度为负3
        #         q = 1.0
        #         a = -3
        #     # 初速度v0
        #     v0 = v
        #     # 当前速度v = v0 + at
        #     v = v0 + a * t
        #     # 移动距离x = v0t + 1/2 * a * t^2
        #     r1 = random.choice(r)
        #     p1 = random.choice(p)
        #     move = r1 * v0 * t + 1 / p1 * a * t * t * q
        #     # 当前位移
        #     if i == 2:
        #         currentdis = (distance - current) / random.choice([3.5, 4.0, 4.5, 5.0])
        #         current += currentdis
        #         track.append(round(currentdis))
        #     elif i == 4:
        #         currentdis = (distance - current) / random.choice([4.0, 5.0, 6.0, 7.0])
        #         current += currentdis
        #         track.append(round(currentdis))
        #     else:
        #         current += move
        #         track.append(round(move))
        #     # 加入轨迹
        #     i = i + 1
        # return track
    def get_slider(self, browser):
        """
        获取滑块
        :return: 滑块对象
        """
        slider = None
        while True:
            try:
                slider = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#slideBlock')))
                break
            except:
                break
        return slider

    def move_to_gap(self, browser, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(browser).click_and_hold(slider).perform()
        time.sleep(0.1)
        while track:
            x = random.choice(track)
            y = random.choice([-2, -1, 0, 1, 2])
            ActionChains(browser).move_by_offset(xoffset=x, yoffset=y).perform()
            track.remove(x)
            t = random.choice([0.02,0.03,0.04,0.05,0.06])
            # time.sleep(t)
        ActionChains(browser).release(on_element=slider).perform()
    def login(self):
        # while True:
        #     self.driver.delete_all_cookies()
        #     currhandle = self.driver.current_window_handle
        while True:
            # try:
            #     # self.driver.switch_to_window(currhandle)
            # except Exception as e:
            #     print(e)
            # try:
            #     verify_Bt = self.wait.until(EC.element_to_be_clickable((By.ID,'slideBlock')))   #按钮是否可点击
            #     verify_Bt.click()
            # except Exception as e:
                # self.driver.refresh()
                # continue
            try:
                # if flag is not 0:
                # iframe = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="tcaptcha_iframe"]')))
                # time.sleep(5)
                # self.driver.switch_to.frame(iframe)     #切换到iframe失败
                #检测是否有滑动验证码,有滑动验证码就滑动
                Sliding_Pic = self.wait.until(EC.presence_of_element_located((By.ID,'slideBg')))
                for i in range(1,20):
                    # page = self.driver.page_source
                    # selector = html.etree.HTML(page)
                    # bg_imgSrc = selector.id('slideBg')[0]
                    bg_imgSrc = self.wait.until(EC.presence_of_element_located((By.ID, 'slideBg'))).get_attribute('src')
                    res = requests.get(bg_imgSrc)
                    with open("./bg_img.jpg","wb") as fp:
                        fp.write(res.content)
                    #计算滑块滑动距离
                    # dist = get_distanct("./bg_img.jpg")


                    bg_img = Image.open("./bg_img.jpg")
                    full_dir = get_full_pic_new(bg_img)
                    print("full_dir1",full_dir)
                    # if full_dir =="../assets/QQloginimgs/7.jpg":
                    #     # print("full_dir2",full_dir)
                    #     self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#e_reload'))).click()
                    #     continue
                    full_img = Image.open(full_dir)
                    dist= get_gap(full_img, bg_img)
                    # dist=get_pos(bg_imgSrc)
                    print("打印滑动距离:",dist)
                    dist = int((dist)/2-34)
                    # dist = int(dist)
                    #获取滑动轨迹
                    print(dist)
                    track = self.get_track(dist)
                    print(track)
                    print(sum(track))
                    err = (dist-sum(track))   #距离修正值
                    print(err)
                    #获取滑块
                    track.append(err)
                    track.append(-(45-i))
                    slide = self.get_slider(self.driver)
                    #滑动滑块
                    self.move_to_gap(self.driver,slide,track)
                    time.sleep(1)
                    slide = self.get_slider(self.driver)
                    if slide:
                        continue
                    else:
                        if len(self.driver.find_elements_by_css_selector("#ptlogin_iframe")):
                            print("帐号或密码不正确")
                            break
                        else:
                            print("滑动验证通过")
                            try:
                                result = WebDriverWait(self.driver, 10).until(EC.alert_is_present())
                                result.accept()
                            # if result:
                            except Exception as E:
                                print(E)
                            break
                    # self.driver.switch_to.frame(self.driver.find_element_by_css_selector("#ptlogin_iframe"))
                    #ptlogin_iframe
                    # err=self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#err_m")))
                    # print(err[0].get_attribute('textContent'))
                    # if len(err) and err[0].get_attribute(
                    #     'textContent') in ['你输入的帐号或密码不正确，请重新输入。','你输入的验证码不正确，请重新输入。']:
                    #     print("你输入的帐号或密码不正确，请重新输入。")
                    # else:
                    #     continue
            except Exception as e:
                print(e)
                print("滑动异常le ")
                # time.sleep(1)
                break
            # break
if __name__=="__main__":
    print("test\n")
    login = tx_test()
    login.login()
