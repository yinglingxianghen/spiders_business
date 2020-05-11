import os

import pymysql
#打开数据库连接
def data_into_db(sql):
    # db = pymysql.connect(host='localhost',user='root',passwd='111111',db='advdb')
    db = pymysql.connect(host='localhost',user='root',passwd='111111',db='oceans')
    cursor = db.cursor()
    li='ttt'
    li=['1',3]
    # a=str(li)
    # sql="insert into spread (id,msgs) value (13,'[\"a\",]')"
    # sql=f'insert into spread (id,msgs) value (18,"{li}")'
    sql2=f'insert into spread (id,msgs) value (18,{li})'
    print(sql2)
    # 'insert into sprea_idea  (msgs) value ("b")'
    # cursor.execute(sql)
    # db.commit()
    # db.close()
    # # cursor.execute('insert into spre_idea  value ("{0}")'.format(a))
    # cursor.execute('select * from sprea_idea')

    #fetchone()方法获取返回对象的单条数据
    # data = cursor.fetchone()
    # print('Database version:{0}'.format(data))

    # results = cursor.fetchall()
    # for i in results:
    #     print(i)
    # print(results[-1])

    #关闭数据库连接
if __name__ == '__main__':
    data_into_db("sql")
    # print(os.path.dirname(os.path.abspath('.')))
    # li='["1",3]'
    # print(eval(li))
