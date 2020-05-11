import json
import random
import telnetlib
import requests
import redis
import schedule
class GetProxies(object):
    def __init__(self):
        self.r = redis.StrictRedis(host='192.168.50.77', port=6379, decode_responses=True,db=1)
        # self.pipe = self.r.pipeline()

    def get_proxy_strict(self,area):
        try:
            ip=requests.get("http://dps.kdlapi.com/api/getdps/?orderid=926699461943661&num=1&area=%s&format=json" %area)
            print(json.loads(ip.text)["data"]["proxy_list"][0]+","+area)
            return json.loads(ip.text)["data"]["proxy_list"][0]+","+area
        except:
            print("log")
            return None

    def get_proxy_casual(self):
        ip = requests.get("http://dps.kdlapi.com/api/getdps/?orderid=926699461943661&num=1&format=json&f_loc=1")
        print(json.loads(ip.text)["data"]["proxy_list"][0])
        return json.loads(ip.text)["data"]["proxy_list"][0]

    def valid_proxy(self,ip,port):
        resu=requests.get("http://dps.kdlapi.com/api/checkdpsvalid?orderid=926699461943661&signature=t3s9qfe4k4bydy67h2hra2m2pvcbfahf&proxy=%s:%d"%(ip,port))
        print(resu.text)

    def test_proxy_letftime(self,proxy):
        resu = requests.get("http://dps.kdlapi.com/api/getdpsvalidtime?orderid=926699461943661&signature=t3s9qfe4k4bydy67h2hra2m2pvcbfahf&proxy=%s"%proxy)
        # %(ip,port)
        print("json.loads(resu.text)",json.loads(resu.text))
        proxy=proxy.split(",")[0]
        left_time=json.loads(resu.text)["data"][proxy]
        if left_time>300:
            return True
        else:
            return False

    def get(self,mode,area=None):
        if mode=="strict":
            proxyli =self.r.lrange(area, 0, 0)
            print("proxy",self.r.lrange(area, 0, 0),proxyli)
            if len(proxyli)==0:
                res0=self.put(mode="strict",area=area)
                if res0=="Empty":
                    print("该城市暂无IP代理")
                    return {"code":-2,"message":"该城市暂无IP代理"}
                return self.get(mode="strict",area=area)
            proxy=proxyli[0]
            self.r.ltrim(area, 1, -1)
            # self.r.lrem(area, 1, proxy)
            return proxy
        elif mode=="loose":
            keys=self.r.keys()
            area=random.choice(keys)
            proxyli = self.r.lrange(area, 0, -1)
            print("proxyli0",proxyli)
            if len(proxyli)==0:
                return self.get(mode="loose")
            return proxyli[0]
        else:
            return "mode error"

    def put(self,mode,area=None):
        if mode=="strict":
            proxy=self.get_proxy_strict(area)
            if proxy==None:
                print("Empty")
                return "Empty"
            self.r.rpush(area, proxy)
            print("r",self.r.lrange(area,0,0))
        elif mode=="loose":
            proxy=self.get_proxy_casual()
            print("proxy",proxy,type(proxy))
            area1=proxy.split(",")[1]
            self.r.rpush(area1, proxy)
            print("r", self.r.lrange(area1, 0, 0))
        else:
            return "mode error"

    def pop_proxy(self):
        keys = self.r.keys()
        print(keys)
        for i in keys:
            print(0,self.r.lrange(i, 0, -1))
            proxyli = self.r.lrange(i,0,-1)
            for j in proxyli:
                if not self.test_proxy_letftime(j):
                    self.r.lrem(i,0,j)
                    self.put(mode="strict",area=i)
            self.put(mode="loose")
            print(1,self.r.lrange(i,0,-1))


    def test_connect(self):
        self.r.rpush("a", "a")
        print(self.r.keys())

    def delete_proxy(self):
        self.r.delete("area")
        print(self.r.keys())

if __name__ == '__main__':
    # GetProxies().test_connect()
    # GetProxies().test_proxy_letftime("120.80.42.45:23903")
    # GetProxies().valid_proxy("120.80.42.45",23903)

    # res1=GetProxies().get(mode="strict",area="南通")
    # print("res1",res1)
    # GetProxies().put(mode="loose")
    # GetProxies().delete_proxy()
    GetProxies().pop_proxy()


    # print(GetProxies().r.lrange("proxies",0,-1))
    # GetInterface().valid_proxy()
    # schedule.every(5).minutes.do(GetProxies().pop_proxy)
    # schedule.every(30).minutes.do(GetProxies().put,"111.72.155.77",17824)
    # schedule.every(1).seconds.do(GetProxies().put,mode="loose")
    # schedule.every(1).seconds.do(GetProxies().test_proxy_letftime,"111.72.155.77",17824)
    # while True:
    #     schedule.run_pending()