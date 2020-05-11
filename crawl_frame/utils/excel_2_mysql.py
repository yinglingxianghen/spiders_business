import datetime

import pandas as pd
from sqlalchemy import create_engine

# 初始化数据库连接，使用pymysql模块
db_info = {'user': 'root',
        'password': '111111',
          'host': 'localhost',
        'port': 3306,
       'database': 'oceans'
         }
# engine = create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s:%(port)d/%(database)s?charset=utf8' % db_info, encoding='utf-8')
# 直接使用下一种形式也可以
def excel_to_mysql(ex_path,table_name):
    engine = create_engine('mysql+pymysql://root:111111@localhost:3306/oceans')
    # 读取本地CSV文件
    df = pd.read_excel(ex_path,encoding="utf-8",sep="\t")

    #将新建的DataFrame储存为MySQL中的数据表，不储存index列(index=False)
    # if_exists:
    # 1.fail:如果表存在，啥也不做
    # 2.replace:如果表存在，删了表，再建立一个新表，把数据插入
    # 3.append:如果表存在，把数据插入，如果表不存在创建一个表！！
    # pd.io.sql.to_sql(df, 'example', con=engine, index=False, if_exists='replace')

    columns0=df.columns.tolist()
    from xpinyin import Pinyin
    p = Pinyin()
    # default splitter is `-`
    columns1=list(map(lambda x:p.get_pinyin(x,""),columns0))
    df.columns=columns1
    rows=df.shape[0]

    dt = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
    df1 = pd.DataFrame({'time': [dt for i in range(rows)]})

    df2 = pd.concat([df,df1],axis=1)
    print(df2)
    df2.to_sql(table_name, con=engine,  index=True, index_label='id',if_exists='replace')