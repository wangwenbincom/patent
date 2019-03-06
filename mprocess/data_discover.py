import json
import sqlite3
from tqdm import tqdm
from cache_database import CacheDB


def push_sells(conn, sells):
    cursor = conn.cursor()
    # cursor.execute('drop table just_test')
    # sql_create = "CREATE TABLE just_test (" \
    #              "id integer PRIMARY KEY AUTOINCREMENT," \
    #              "pid text," \
    #              "title text," \
    #              "jieba_kw text," \
    #              "ptype text," \
    #              "cond text," \
    #              "time text," \
    #              "contact text" \
    #              ")"
    # cursor.execute(sql_create)
    # conn.commit()
    count = 0

    for sell in tqdm(sells):
        # pprint(sell)
        id_ = sell['pid']
        title_ = sell['title']
        jieba_kw_ = ','.join(sell['jieba_kw']) if sell['jieba_kw'] != [] else "null"
        ptype_ = sell['ptype'] if sell['ptype'] != '' else "null"
        cond_ = sell['cond'] if sell['cond'] != '' else "null"
        time_ = sell['time']
        contact_ = sell['contact']
        sql_insert = "INSERT INTO just_test(pid,title,jieba_kw,ptype,cond,time,contact)" \
                     " VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(
            id_, title_, jieba_kw_, ptype_, cond_, time_, contact_)
        # print(sql_insert)

        cursor.execute(sql_insert)
        count += 1

    conn.commit()





fmt_sells = json.loads(open('data/temp_sells.json','r',encoding='u8').read())
fmt_buys = json.loads(open('data/temp_sells.json','r',encoding='u8').read())


# conn = sqlite3.connect('data/patent.db')
# push_sells(conn,fmt_sells)

cdb = CacheDB('data/patent.db')


