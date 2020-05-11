from pymongo import MongoClient

conn = MongoClient('127.0.0.1', 27017)
db = conn.test01  #连接mydb数据库，没有则自动创建
my_set = db.test_set #使用test_set集合，没有则自动创建
my_set.insert_one({"sex":"zhangsan","xx":18})
my_set.insert_many([{"grade":"zhangsan","tall":18},{"height":"wangwu","shoe":19}])
print(my_set.find_one({"age":18}))
for i in my_set.find():
    print(i)

tubiao420 = self.db.tubiao420
tubiao420.insert(json.loads(res.text)["data"]["statistics"])
for i in tubiao420.find():
    print(i)