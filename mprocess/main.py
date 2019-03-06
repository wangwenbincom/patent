import sqlite3
from datetime import datetime, timedelta
from itertools import groupby
from segment import Segment
from structured import Structured
import json
from pprint import pprint
# from IPProxy import start_service
from extend import LoadElasticSearch,Extend
from crawl import CwralPatent
from cache_database import CacheDB
import time
from apscheduler.schedulers.background import BackgroundScheduler


class MsgProcess:
    def __init__(self, interval, segm):
        self.db_name = 'data/patent.db'
        self.interval = interval
        self.segm = segm
        self.conn = sqlite3.connect(self.db_name)
        # start_service()

    def __del__(self):
        self.conn.close()


    def getMsgFromDB(self):
        cursor = self.conn.cursor()
        sql = 'select * from cache'
        raw_data = [line for line in cursor.execute(sql)]
        self.conn.close()
        return raw_data

    def combine_block(self, raw_data):
        block = list()
        for key, lines in groupby(raw_data, key=lambda x: x[1]):
            content = ''
            order_by_id = sorted(lines, key=lambda x: x[0])
            old = order_by_id[0][0]-1
            user_id = order_by_id[0][1]
            time = datetime.fromtimestamp(order_by_id[0][2]).strftime('%Y-%m-%d')
            for line in order_by_id:
                if line[0] == old+1:
                    content += line[3]
                    old = line[0]
                    # print(old, line[0])
                else:
                    user_id = line[1]
                    time = datetime.fromtimestamp(line[2]).strftime('%Y-%m-%d')
                    block.append([user_id, time, content])
                    # print(old,line[0])
                    # pprint([line[0], user_id, time, content])

                    content = line[3]
                    old = line[0]
            block.append([user_id, time, content])
            # pprint([user_id, time, content])

        return block

    def distinct_data(self, trade, data):
        dstc = list()
        if trade == 'sell':
            sell_ids = set()
            for sell in sorted(data,key=lambda k:k['time'],reverse=True):
                id = sell['pid'] + str(sell['contact'])
                if id in sell_ids:
                    continue
                else:
                    sell_ids.add(id)
                    dstc.append(sell)

            print(len(list(sell_ids)))
            return dstc

        if trade == 'buy':
            buy_ids = set()
            print(data)
            for buy in sorted(data,key=lambda k:k['time'],reverse=True):
                try:
                    uni = str(buy['contact']) + buy['hand_kw'][0] + buy['hand_kw'][-1]
                except:
                    uni = str(buy['contact'])

                if uni in buy_ids:
                    continue
                else:
                    buy_ids.add(uni)
                    dstc.append(buy)
            print(len(list(buy_ids)))
            return dstc

    def save_data(self, filename, data):
        open(filename, 'w', encoding='u8').write(json.dumps(data, ensure_ascii=False))

    def load_data(self, filename):
        with open(filename, 'r', encoding='u8') as f:
            return json.loads(f.read())

    def sell_extend_to_es(self, fmt_sells, cdb):
        # Distinct
        dstc_sells = self.distinct_data(trade='sell', data=fmt_sells)
        print('dstc_sells',dstc_sells)

        # Crawl Patent Summary
        patent_ids = [sell['pid'] for sell in dstc_sells]
        cp = CwralPatent(patent_ids)
        cp.baiten()

        # Extend
        print('extend_sell')
        ext = Extend()
        ext_sells = ext.extend_sell(dstc_sells)
        print('ext_sells', ext_sells)
        cdb.push_entend_sells(ext_sells)

        # ES server
        es_sell = LoadElasticSearch(index='sell', doc_type='content')
        # es_sell.set_config()
        es_sell.insert_data(ext_sells, print_result=True)

    def bus_extend_to_es(self, fmt_buys, cdb):
        # Distinct
        dstc_buys = self.distinct_data(trade='buy', data=fmt_buys)
        print('dstc_buys', dstc_buys)

        # Extend
        print('extend_buy')
        ext = Extend()
        ext_buys = ext.extend_buy(dstc_buys)
        print('ext_buys', ext_buys)
        cdb.push_extend_buys(ext_buys)

        # ES server
        es_buy = LoadElasticSearch(index='buy', doc_type='content')
        # es_buy.set_config()
        es_buy.insert_data(ext_buys, print_result=True)


    def mprocess(self):
        # print('Run Process')
        # raw_data = self.getMsgFromDB()
        # blocks = self.combine_block(raw_data)
        #
        # # Word Segmentation
        # seg = Segment(is_print=False,segm='jieba')
        # buys = seg.get_buy(blocks)
        # print("------buys-----\n")
        # pprint(buys)
        #
        # sells = seg.get_sell(blocks)
        # print("-----sells-----\n")
        # pprint(sells)
        #
        # # Format
        # struct = Structured()
        # print('Run format buys')
        # fmt_buys = struct.format_buys(buys)
        # print('Run format sells')
        # fmt_sells = struct.format_sells(sells)
        #
        # # Temp save in disk
        # self.save_data('data/temp_buys.json', fmt_buys)
        # self.save_data('data/temp_sells.json', fmt_sells)
        #
        # # Load data for test
        # fmt_buys = self.load_data('data/temp_buys.json')
        fmt_sells = self.load_data('data/temp_sells.json')
        #
        # # Cache in database
        cdb = CacheDB('data/patent.db')
        # cdb.push_database_buys(fmt_buys)
        # cdb.push_database_sells(fmt_sells)
        #
        # #Extend and ES
        # self.bus_extend_to_es(fmt_buys, cdb)
        self.sell_extend_to_es(fmt_sells, cdb)


if __name__ == '__main__':
    mproc = MsgProcess(interval=2,segm='jieba')
    mproc.mprocess()
    # while(1):
    #     mproc.mprocess()
    #     run_time = 60*60
    #     time.sleep(run_time)


    # scheduler = BackgroundScheduler()
    # scheduler.add_job(mproc.mprocess,"interval",seconds=1)
    # scheduler.start()