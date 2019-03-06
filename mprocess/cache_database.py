import sqlite3
from pprint import pprint


class CacheDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)

    def push_database_sells(self, sells):
        cursor = self.conn.cursor()

        sql_create = "CREATE TABLE temp_sells (" \
                     "id integer PRIMARY KEY AUTOINCREMENT," \
                     "pid text," \
                     "title text," \
                     "jieba_kw text," \
                     "ptype text," \
                     "cond text," \
                     "time text," \
                     "contact text" \
                     ")"
        cursor.execute(sql_create)
        self.conn.commit()
        # flag_set = set()
        # for sell in sorted(sells,reverse=True,key=sells.index):
        #     if sell['pid']+sell['contact'] in flag_set:
        #         continue
        #     else:
        #         flag_set.add(sell['pid']+sell['contact'])
        for sell in sells:
            id_ = sell['pid']
            title_ = sell['title']
            jieba_kw_ = ','.join(sell['jieba_kw']) if sell['jieba_kw'] != [] else "null"
            ptype_ = sell['ptype'] if sell['ptype'] != '' else "null"
            cond_ = sell['cond'] if sell['cond'] != '' else "null"
            time_ = sell['time']
            contact_ = sell['contact']
            sql_insert = "INSERT INTO temp_sells(pid,title,jieba_kw,ptype,cond,time,contact)" \
                         " VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(
                id_, title_, jieba_kw_, ptype_, cond_, time_, contact_)
            print(sql_insert)
            try:
                cursor.execute(sql_insert)
            except:
                pass
        self.conn.commit()

    def push_database_buys(self, buys):
        cursor = self.conn.cursor()

        sql_create = "CREATE TABLE temp_buys (" \
                     "id integer PRIMARY KEY AUTOINCREMENT," \
                     "raw text," \
                     "hand_kw text," \
                     "jieba_kw text," \
                     "ptype text," \
                     "cond text," \
                     "other text," \
                     "time text," \
                     "contact text" \
                     ")"
        cursor.execute(sql_create)
        self.conn.commit()
        for buy in buys:
            raw_ = buy['raw']
            hand_kw_ = ','.join(buy['hand_kw']).translate({ord(k): None for k in " []'"}) if buy[
                                                                                                 'hand_kw'] != [] else "null"
            jieba_kw_ = ','.join(buy['jieba_kw']) if buy['jieba_kw'] != [] else "null"
            ptype_ = buy['ptype'] if buy['ptype'] != '' else "null"
            cond_ = buy['cond'] if buy['cond'] != '' else "null"
            other_ = ','.join(buy['other']) if buy['other'] != [] else "null"
            time_ = buy['time']
            contact_ = buy['contact']
            sql_insert = "INSERT INTO temp_buys(raw, hand_kw,jieba_kw,ptype,cond,other,time,contact)" \
                         " VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')".format(
                raw_, hand_kw_, jieba_kw_, ptype_, cond_, other_, time_, contact_)
            print(sql_insert)
            try:
                cursor.execute(sql_insert)
            except Exception as e:
                print(e)
        self.conn.commit()

    def push_entend_sells(self, ext_sells):
        cursor = self.conn.cursor()
        # sell_new = {k['pid']+k['contact'] for k in ext_sells}
        # sell_exist = {x[0]+x[1] for x in cursor.execute('select pid,contact from ext_sells')}
        # sell_update = sell_exist & sell_new
        # for sell_n in sell_update:
        #     cursor.execute('delete from ext_sells where pid={} and contact={}'.format(
        #         sell_n[:13],sell_n[13:]
        #     ))
        # self.conn.commit()

        cursor.execute('drop table temp_sells')
        sql_create = "CREATE TABLE ext_sells (" \
                     "id integer PRIMARY KEY AUTOINCREMENT," \
                     "pid text," \
                     "title text," \
                     "jieba_kw text," \
                     "ptype text," \
                     "cond text," \
                     "time text," \
                     "contact text," \
                     "summary text," \
                     "sum_key text" \
                     ")"
        cursor.execute(sql_create)
        self.conn.commit()

        for sell in ext_sells:
            pprint(sell)
            id_ = sell['pid']
            title_ = sell['title']
            jieba_kw_ = ','.join(sell['jieba_kw']) if sell['jieba_kw'] != [] else "null"
            ptype_ = sell['ptype'] if sell['ptype'] != '' else "null"
            cond_ = sell['cond'] if sell['cond'] != '' else "null"
            time_ = sell['time']
            contact_ = sell['contact']
            summary_ = sell['summary']
            sum_key_ = ','.join(sell['sum_key'])
            sql_insert = "INSERT INTO ext_sells(pid,title,jieba_kw,ptype,cond,time,contact,summary,sum_key)" \
                         " VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                id_, title_, jieba_kw_, ptype_, cond_, time_, contact_, summary_, sum_key_)
            print(sql_insert)
            try:
                cursor.execute(sql_insert)
            except Exception as e:
                print(e)

        self.conn.commit()

    def push_extend_buys(self, ext_buys):
        cursor = self.conn.cursor()

        cursor.execute('drop table temp_buys')
        sql_create = "CREATE TABLE ext_buys (" \
                     "id integer PRIMARY KEY AUTOINCREMENT," \
                     "raw text," \
                     "hand_kw text," \
                     "jieba_kw text," \
                     "ptype text," \
                     "cond text," \
                     "other text," \
                     "time text," \
                     "contact text," \
                     "synonym text" \
                     ")"
        cursor.execute(sql_create)
        self.conn.commit()

        for buy in ext_buys:
            pprint(buy)
            raw_ = buy['raw']
            hand_kw_ = ','.join(buy['hand_kw']).translate({ord(k): None for k in " []'"}) if buy[
                                                                                                 'hand_kw'] != [] else "null"
            jieba_kw_ = ','.join(buy['jieba_kw']) if buy['jieba_kw'] != [] else "null"
            ptype_ = buy['ptype'] if buy['ptype'] != '' else "null"
            cond_ = buy['cond'] if buy['cond'] != '' else "null"
            other_ = ','.join(buy['other']) if buy['other'] != [] else "null"
            time_ = buy['time']
            contact_ = buy['contact']
            synonym_ = ','.join(buy['synonym'])
            sql_insert = "INSERT INTO ext_buys(raw, hand_kw,jieba_kw,ptype,cond,other,time,contact,synonym)" \
                         " VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                raw_, hand_kw_, jieba_kw_, ptype_, cond_, other_, time_, contact_, synonym_)
            print(sql_insert)
            cursor.execute(sql_insert)
        self.conn.commit()
