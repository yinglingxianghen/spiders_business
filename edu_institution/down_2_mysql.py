#coding:utf-8
from rediscluster import StrictRedisCluster
from sqlalchemy import create_engine, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Sequence, MetaData, Table
from sqlalchemy.orm import relationship, sessionmaker
# from sqlalchemy.sql import exists
import traceback,datetime,time
# from logconfs.config import log
from logconfs.con_vars import conf
import redis
user = conf["mysql"]["user"]
pwd = conf["mysql"]["pwd"]
ip = conf["mysql"]["ip"]
port = conf["mysql"]["port"]
db = conf["mysql"]["db"]
engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4' % (user, pwd, ip, port, db))
Base = declarative_base()
md = MetaData(bind=engine)
Session = sessionmaker(bind=engine)
dbsession = Session()
redis_nodes1 = [{'host': conf['proxy']['host1'], 'port': int(conf['proxy']['port1'])},
                {'host': conf['proxy']['host1'], 'port': int(conf['proxy']['port2'])},
                {'host': conf['proxy']['host1'], 'port': int(conf['proxy']['port3'])},
                {'host': conf['proxy']['host1'], 'port': int(conf['proxy']['port4'])}]
redisconn1 = StrictRedisCluster(startup_nodes=redis_nodes1, decode_responses=True)
# redisconn1 = StrictRedisCluster(startup_nodes=redis_nodes1, decode_responses=True,password=conf['proxy']['password'])

# redisconn1 = redis.Redis(host=conf['proxy']['host'], port=int(conf['proxy']['port']), decode_responses=True)

class XueXiPeiXun(Base):    __table__ = Table("meituan_xuexipeixun", md, autoload=True)
class QuanGuoXiaoWai(Base):
    __table__ = Table("quanguoxiaowai", md, autoload=True)
class JiaoYuBao(Base):
    __table__ = Table("jiaoyubao", md, autoload=True)
class ZhongHuaKaoShi(Base):
    __table__ = Table("zhonghuakaoshi", md, autoload=True)

class Edu_All(Base):
    __table__ = Table("edu_all", md, autoload=True)
class OrFile(Base):
    __table__ = Table("organizationfile", md, autoload=True)

# addtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# obj0 = dbsession.merge(XueXiPeiXun(name="1",area="1",phone="2",addtime=addtime))
# dbsession.add(obj0)
# dbsession.commit()

# obj1 = dbsession.query(XueXiPeiXun).filter(XueXiPeiXun.name.notin_("1")).all()
# # obj1 = dbsession.query(XueXiPeiXun).filter(XueXiPeiXun.name.in_(["1","2"])).all()
# for i in obj1:
#     print(i.__dict__)

# print(dbsession.query(XueXiPeiXun).filter(XueXiPeiXun.area=="文泽路99号2701室",XueXiPeiXun=="申1士留学").first())
def save_meituan_xuexipeixun(name,area,phone,addtime,province,city,district,lng,lat):
    try:
        exist=dbsession.query(XueXiPeiXun).filter(XueXiPeiXun.area==area).first()
        dbsession.commit()
        if not exist:
            obj0=XueXiPeiXun(name=name,area=area,phone=phone,addtime=addtime,province=province,city=city,district=district,longitude=lng,latitude=lat)
            dbsession.add(obj0)
            dbsession.commit()
        else:
            obj0=dbsession.query(XueXiPeiXun).filter(XueXiPeiXun.area==area).first()
            obj0.province=province
            obj0.city=city
            obj0.district=district
            obj0.longitude = lng
            obj0.latitude = lat
            obj0.name=name
            obj0.phone=phone
            obj0.updatetime=addtime
            dbsession.commit()
        # dbsession.close()
    except Exception as e:
        dbsession.rollback()
        # # dbsession.close()
        # log().warning({"msg":"插表失败"+str(repr(traceback.format_exc())).replace("\"","").replace("\'","")})
        # print(traceback.format_exc())
def save_jioyubao(name,area,phone,addtime,province,city,district,lng,lat):
    try:
        exist=dbsession.query(JiaoYuBao).filter(JiaoYuBao.area==area).first()
        dbsession.commit()
        if not exist:
            obj0=JiaoYuBao(name=name,area=area,phone=phone,addtime=addtime,province=province,city=city,district=district,longitude=lng,latitude=lat)
            dbsession.add(obj0)
            dbsession.commit()
        else:
            obj0=dbsession.query(JiaoYuBao).filter(JiaoYuBao.area==area).first()
            obj0.province = province
            obj0.city = city
            obj0.district = district
            obj0.longitude = lng
            obj0.latitude = lat
            obj0.name=name
            obj0.phone=phone
            obj0.updatetime=addtime
            dbsession.commit()
        # dbsession.close()
    except Exception as e:
        dbsession.rollback()
        # # dbsession.close()
        # log().warning({"msg":"插表失败"+str(repr(traceback.format_exc())).replace("\"","").replace("\'","")})
        print(traceback.format_exc())

def save_zhonghua(name,area,phone,addtime,province,city,district):
    try:
        exist=dbsession.query(ZhongHuaKaoShi).filter(ZhongHuaKaoShi.area==area).first()
        dbsession.commit()
        if not exist:
            obj0=ZhongHuaKaoShi(name=name,area=area,phone=phone,addtime=addtime,province=province,city=city,district=district)
            dbsession.add(obj0)
            dbsession.commit()
        else:
            obj0=dbsession.query(ZhongHuaKaoShi).filter(ZhongHuaKaoShi.area==area).first()
            obj0.province = province
            obj0.city = city
            obj0.district = district
            obj0.name=name
            obj0.phone=phone
            obj0.updatetime=addtime
            dbsession.commit()
        # dbsession.close()
    except Exception as e:
        # dbsession.rollback()
        # # dbsession.close()
        # log().warning({"msg":"插表失败"+str(repr(traceback.format_exc())).replace("\"","").replace("\'","")})
        pass

def save_quanguoxiaowai(name,shelishijian,tongyidaima,zhucedizhi,peixunneirong,area,farendaibiaoxingming,xiaozhangfuzeren,jubanzhemingcheng,jubanzheshuxing,banxuezizhi,banxuexukezhenghao,fazhengjiguan,farendengjibumen,peixunleibie,jianzhumianji,addtime,province,city,district,phone):
    try:
        exist=dbsession.query(QuanGuoXiaoWai).filter(QuanGuoXiaoWai.area==area).first()
        dbsession.commit()
        if not exist:
            obj0=QuanGuoXiaoWai(name=name,shelishijian=shelishijian,tongyidaima=tongyidaima,zhucedizhi=zhucedizhi,peixunneirong=peixunneirong,area=area,farendaibiaoxingming=farendaibiaoxingming,xiaozhangfuzeren=xiaozhangfuzeren,jubanzhemingcheng=jubanzhemingcheng,jubanzheshuxing=jubanzheshuxing,banxuezizhi=banxuezizhi,banxuexukezhenghao=banxuexukezhenghao,fazhengjiguan=fazhengjiguan,farendengjibumen=farendengjibumen,peixunleibie=peixunleibie,jianzhumianji=jianzhumianji,addtime=addtime,province=province,city=city,district=district,phone=phone)
            dbsession.add(obj0)
            dbsession.commit()
        else:
            obj0=dbsession.query(QuanGuoXiaoWai).filter(QuanGuoXiaoWai.area==area).first()
            obj0.province = province
            obj0.city = city
            obj0.district = district
            obj0.phone=phone
            obj0.name = name
            obj0.shelishijian = shelishijian
            obj0.tongyidaima = tongyidaima
            obj0.zhucedizhi = zhucedizhi
            obj0.peixunneirong = peixunneirong
            obj0.area = area
            obj0.farendaibiaoxingming = farendaibiaoxingming
            obj0.xiaozhangfuzeren = xiaozhangfuzeren
            obj0.jubanzhemingcheng = jubanzhemingcheng
            obj0.jubanzheshuxing = jubanzheshuxing
            obj0.banxuezizhi = banxuezizhi
            obj0.banxuexukezhenghao = banxuexukezhenghao
            obj0.fazhengjiguan = fazhengjiguan
            obj0.farendengjibumen = farendengjibumen
            obj0.peixunleibie = peixunleibie
            obj0.jianzhumianji = jianzhumianji
            obj0.updatetime=addtime
            dbsession.commit()
        # dbsession.close()
    except Exception as e:
        # dbsession.rollback()
        # # dbsession.close()
        # log().warning({"msg":"插表失败"+str(repr(traceback.format_exc())).replace("\"","").replace("\'","")})
        pass



def save_four_toall(table):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for i in dbsession.query(table).filter(or_(table.addtime<=dt,table.updatetime<=dt)).all():
        print(i)
        try:
            exist = dbsession.query(Edu_All).filter(Edu_All.name == i.name,Edu_All.area == i.area,Edu_All.phone == i.phone,Edu_All.district==i.district).first()
            dbsession.commit()
            if not exist:
                obj0 = Edu_All(name=i.name, area=i.area, phone=i.phone, addtime=dt, province="浙江", city="杭州",district=i.district,longitude=i.longitude,latitude=i.latitude)
                dbsession.add(obj0)
                dbsession.commit()
            else:
                exist.name = i.name
                exist.area = i.area
                exist.phone = i.phone
                exist.province = "浙江"
                exist.city = "杭州"
                exist.district = i.district
                exist.longitude = i.longitude
                exist.latitude = i.latitude
                exist.updatetime = dt
                dbsession.commit()
        except Exception as e:
            print(traceback.format_exc())
            dbsession.rollback()

def save_quanguo_toall(table):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for i in dbsession.query(table).filter(or_(table.addtime<=dt,table.updatetime<=dt)).all():
        try:
            exist = dbsession.query(Edu_All).filter(Edu_All.name == i.name,Edu_All.area == i.area,Edu_All.phone == i.phone,Edu_All.district==i.district).first()
            dbsession.commit()
            if not exist:
                obj0=Edu_All(name=i.name,shelishijian=i.shelishijian,tongyidaima=i.tongyidaima,zhucedizhi=i.zhucedizhi,peixunneirong=i.peixunneirong,area=i.area,farendaibiaoxingming=i.farendaibiaoxingming,xiaozhangfuzeren=i.xiaozhangfuzeren,jubanzhemingcheng=i.jubanzhemingcheng,jubanzheshuxing=i.jubanzheshuxing,banxuezizhi=i.banxuezizhi,banxuexukezhenghao=i.banxuexukezhenghao,fazhengjiguan=i.fazhengjiguan,farendengjibumen=i.farendengjibumen,peixunleibie=i.peixunleibie,jianzhumianji=i.jianzhumianji,addtime=dt,province=i.province,city=i.city,district=i.district,phone=i.phone)
                dbsession.add(obj0)
                dbsession.commit()
            else:
                exist.province = i.province
                exist.city = i.city
                exist.district = i.district
                exist.phone = i.phone
                exist.name = i.name
                exist.shelishijian = i.shelishijian
                exist.tongyidaima = i.tongyidaima
                exist.zhucedizhi = i.zhucedizhi
                exist.peixunneirong = i.peixunneirong
                exist.area = i.area
                exist.farendaibiaoxingming = i.farendaibiaoxingming
                exist.xiaozhangfuzeren = i.xiaozhangfuzeren
                exist.jubanzhemingcheng = i.jubanzhemingcheng
                exist.jubanzheshuxing = i.jubanzheshuxing
                exist.banxuezizhi = i.banxuezizhi
                exist.banxuexukezhenghao = i.banxuexukezhenghao
                exist.fazhengjiguan = i.fazhengjiguan
                exist.farendengjibumen = i.farendengjibumen
                exist.peixunleibie = i.peixunleibie
                exist.jianzhumianji = i.jianzhumianji
                exist.updatetime = dt
                dbsession.commit()
        except Exception as e:
            pass

def save_img(name,area,img,addtime):
    try:
        edu_exist=dbsession.query(Edu_All).filter(Edu_All.name==name,Edu_All.area==area).first()
        dbsession.commit()
        if edu_exist:
            e_id=edu_exist.id
            file_exit=dbsession.query(OrFile).filter(OrFile.organizationid==e_id,OrFile.url==img).first()
            if file_exit==None:
                obj0=OrFile(organizationid=e_id,url=img,type=1,status=1,creationtime=addtime)
                dbsession.add(obj0)
                dbsession.commit()

    except Exception as e:
        dbsession.rollback()

def save_video(name,area,video,addtime):
    try:
        edu_exist = dbsession.query(Edu_All).filter(Edu_All.name == name, Edu_All.area == area).first()
        dbsession.commit()
        if edu_exist:
            e_id = edu_exist.id
            file_exit = dbsession.query(OrFile).filter(OrFile.organizationid == e_id, OrFile.url == video).first()
            if file_exit == None:
                obj0 = OrFile(organizationid=e_id, url=video, type=2, status=1, creationtime=addtime)
                dbsession.add(obj0)
                dbsession.commit()
    except Exception as e:
        dbsession.rollback()

# save_four_toall(ZhongHuaKaoShi)
# save_quanguo_toall(QuanGuoXiaoWai)
# save_four_toall(JiaoYuBao)
# save_four_toall(XueXiPeiXun)

# save_meituan_xuexipeixun("33333333333333333","凤起路334号同方财富大厦808室","泽羲书苑专业书法培训中心",dt)
# save_zhonghua("上海竞思素质教育培训中心", "上海市普陀区苏河汇113", "15000411174",dt)
# "教育宝|/edu/hzbst/杭州百师堂外国语专修学校|百师堂凤起路校区、学院路校区、古墩路校区|400-029-0997转9618|2020-01-06 18:07:09"
# dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# a=None
# save_jioyubao('name','area','phone',dt,'province','city','district',a,a)
#     print("111")
# except:
#     print("222")
#     dbsession.rollback()
# save_quanguoxiaowai("1","2","3","3","3","3","3","3","3","3","3","3","3","3","3",dt)
# img='https://p1.meituan.net/education/259b5724c1b755a67ddbdfec321293ef2786096.png%40640w_480h_1e_1c_1l%7Cwatermark%3D1%26%26r%3D1%26p%3D9%26x%3D2%26y%3D2%26relative%3D1%26o%3D20'
# file_exit=dbsession.query(OrFile).filter(OrFile.organizationid==4496,OrFile.url==img).first()
# print("file_exit",file_exit.id)