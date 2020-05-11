# -*- coding: utf-8 -*-
import random
from selenium import webdriver

import logging

from interactors import BaseSpider

que = []
tasks = []

# logger = logging.getLogger(__name__)
# logger.warning("This is a warning")
class CblogsSpider(BaseSpider):
    name = 'cblogs'
    allowed_domains = ['https://ad.oceanengine.com/pages/login/index.html']
    start_urls = ['https://ad.oceanengine.com/pages/login/index.html']

    def getcode(self, response):
        verify_code = self.spider_context.wait_for_verify_code(response)
        return verify_code

    def start_requests(self):
        User_Agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0"]
        url = "https://www.cnblogs.com/"
        options = webdriver.ChromeOptions()
        options.add_argument('User-Agent=' + random.choice(User_Agents))
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        options.add_argument('--disable-extensions')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get(url)
        # res=Selector(self.driver.get(url).source_page)
        # logger.info(item["title"],item["content"])

        for i in range(1,4):
            title=self.driver.find_element_by_css_selector("#post_list>div:nth-child("+str(i)+")>div.post_item_body>h3>a").text
            content=self.driver.find_element_by_xpath("//*[@id='post_list']/div["+str(i)+"]/div[2]/p").text
            # item["title"]=WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='post_list']/*/div[2]/h3/a")))
            # item["content"]=WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='post_list']/div[1]/div[2]/p/text()"))).get_attribute('textContent')
            print("item",title,content)
            # yield item

    # def callback(self):
    #     # task=que.pop(1)
    #     # spider_name = task.get("spider_name")
    #     credentials = pika.PlainCredentials(username="dev-spider",password="dev-spider")
    #     connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.50.221', port=5672,credentials=credentials,virtual_host='spider'))
    #     channel = connection.channel()
    #
    #     # response = channel.basic_get(queue='topic_logs1', auto_ack=False)
    #     # print(response.getBody)
    #     # channel.basic_ack(delivery_tag=method.delivery_tag, auto_ack=False)
    #
    #     channel.exchange_declare(exchange='topic_logs')
    #     # channel.exchange_declare(exchange='topic_logs',type='topic')
    #     result = channel.queue_declare(queue='topic_logs1')
    #     queue_name = result.method.queue
    #     binding_keys = ['disk.error', 'disk.warning']
    #     # for binding_key in binding_keys:
    #     #     channel.queue_bind(exchange='topic_logs',
    #     #                        queue='topic_logs1',
    #     #                        routing_key=binding_key)
    #     channel.queue_bind(exchange='topic_logs',queue='topic_logs1',routing_key="disk.error")
    #     print('[*] Waiting for logs. To exit press CTRL+C')
    #     def test(ch, method, body):
    #         # print("%s [x] Received %r" % (datetime.datetime.now(), body,))
    #         # time.sleep(1)
    #         # print("%s [x] Finished %r" % (datetime.datetime.now(), body,))
    #         # ch.basic_ack(delivery_tag=method.delivery_tag)
    #         response = ch.basic_get(queue='topic_logs1', auto_ack=False)[2]
    #         print(response)
    #         channel.basic_ack(delivery_tag=method.delivery_tag,multiple=True)
    #
    #     def callback(ch, method, properties, body):
    #         # t = threading.Thread(target=test, args=(ch, method, body))
    #         # t.start()
    #         test(ch, method, body)
    #
    #     channel.basic_qos(prefetch_count=1)  # 缓冲区的数量
    #     channel.basic_consume(auto_ack=False,on_message_callback=callback,queue='topic_logs1')
    #     channel.start_consuming()
    #
    #     # d = self.process.crawl(spider_name)
    #     d.addBoth(self.__spider_exit__)