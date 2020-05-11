from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql+pymysql://root:111111@127.0.0.1:3306/oceans",encoding="utf-8", echo=True, max_overflow=5)
# engine = create_engine("mysql+pymysql://root:111111@127.0.0.1:3306/oceans",encoding="utf-8", echo=True, max_overflow=5)
# 连接mysql数据库，echo为是否打印结果

Base = declarative_base()  # 生成orm基类

class Ocean_Test_Adgs(Base):
    __tablename__ = "ocean_test_adgs"
    id = Column(Integer, primary_key=True,autoincrement=True)
    budget = Column(String(64),comment="组预算")
    show_cnt = Column(String(64),comment="展示")
    click_cnt = Column(String(64),comment="点击数")
    stat_cost = Column(String(64),comment="花费")
    convert_cnt = Column(String(64),comment="转化数")
    cpc_platform = Column(String(64),comment="cpc")
    cpm_platform = Column(String(64),comment="cpm")
    conversion_cost = Column(String(64),comment="转化成本")
    conversion_rate = Column(String(64),comment="转化率")
    click_start_rate = Column(String(64),comment="点击率")
    campaign_name = Column(String(64),comment="广告组名称")
    campaign_status = Column(Integer(),comment="广告组状态")
    landing_type_name = Column(String(64),comment="推广目的")


# Base.metadata.create_all(engine)
# DBSession = sessionmaker(bind=engine)
# session = DBSession()
# newuser0=Admins111111(username="a",password="aaa")
# session.add(newuser0)
# session.commit()
# print("chengg")
# 父类Base调用所有继承他的子类来创建表结构
# if __name__ == '__main__':
      # 创建表结构