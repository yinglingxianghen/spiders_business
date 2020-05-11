# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, Table
from sqlalchemy.orm import relationship, sessionmaker
from logconfs_bak.con_vars import conf

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

class Article_Category(Base):
    __table__ = Table("article_category", md, autoload=True)  # 自动加载表结构

def get_category_id(name):
    return dbsession.query(Article_Category).filter(Article_Category.name == name).first().id

a={"a":"A","B":"BBB"}
for i in a.items():
    print(i)

lists=["安全新闻","各地动态"]
print(dict({get_category_id(i):i} for i in lists))

