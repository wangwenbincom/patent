import json
from itertools import chain
import elasticsearch
import jieba
import synonyms




class LoadElasticSearch:
    def __init__(self, index, doc_type):
        self.index = index
        self.doc_type = doc_type
        self.es_client = LoadElasticSearch.get_es_servers()


    @staticmethod
    def get_es_servers():
        es_servers = [{
            "host": "localhost",
            "port": "9200"
        }]
        es_client = elasticsearch.Elasticsearch(hosts=es_servers)
        return es_client

    def set_config(self):
        setting = {
            "index": {
                "analysis": {
                    "analyzer": "ik_max_word",
                    "search_analyzer": "ik_max_word"
                },
            }
        }

        self.es_client.indices.delete(index=self.index, ignore=404)

        mapping = json.loads(open('data/mapping.json', 'r', encoding='utf-8').read())['%s_mapping' % self.index]
        if not self.es_client.indices.exists(index=self.index):
            self.es_client.indices.create(index=self.index, ignore=400)
            self.es_client.indices.close(index=self.index)
            self.es_client.indices.put_settings(index=self.index, body=setting)
            self.es_client.indices.open(index=self.index)
            self.es_client.indices.put_mapping(index=self.index, doc_type=self.doc_type, body=mapping)
            open('checkpoint.json', 'w').write(json.dumps(list({})))

    def insert_data(self, data, print_result=False):
        for adata in data:
            result = self.es_client.index(index=self.index, doc_type=self.doc_type, body=adata)
            if print_result:
                print(adata)
                print(result)



class Extend:
    def __init__(self):
        self.stop_words = set([line.strip() for line in open('data/stopwords.txt', 'r', encoding='u8').readlines()])

        # self.summary_dict = dict((tuple(json.loads(line, encoding='u8').items())[0] for line in
        #                           open('data/patent_summary.data', 'r', encoding='u8',
        #                                errors='ignore').readlines()))
        # self.conn = sqlite3.connect('data/patent.db')

    def load_patent_summary(self):
        import sqlite3
        conn = sqlite3.connect('data/patent.db')
        cursor = conn.cursor()
        sql = 'select * from patent_summary'
        return {s[0]:s[1] for s in cursor.execute(sql)}


    def load_data_from_troop(self, is_exist=False):
        if is_exist:
            buys = json.loads(open('search_buys.json', 'r', encoding='u8').read())
            sells = json.loads(open('search_sells.json', 'r', encoding='u8').read())
        else:
            buy_fname = '../data/all_buys.json'
            sell_fname = '../data/all_sells.json'

            buys = json.loads(open(buy_fname, 'r', encoding='u8').read())
            sells = json.loads(open(sell_fname, 'r', encoding='u8').read())

        return buys, sells


    def extend_sell(self, fsells):
        sells = list()
        summary_dict = self.load_patent_summary()
        for fsell in fsells:
            try:
                fsell['summary'] = summary_dict[fsell['pid']]
                fsell['sum_key'] = list(set(jieba.lcut(fsell['summary'])) - self.stop_words)
            except:
                fsell['summary'] = ""
                fsell['sum_key'] = []
            sells.append(fsell)
        return sells


    def get_synonyms(self, hand_, jie_cut_, max_num=5):
        synonyms_word = list(chain(*[synonyms.nearby(word)[0][1:1 + 3 // len(hand_)] for word in hand_ + jie_cut_]))
        return sorted(list(set(synonyms_word)), key=synonyms_word.index)[:max_num]


    def extend_buy(self, fbuys):
        buys = list()
        for fbuy in fbuys:
            fbuy['synonym'] = self.get_synonyms(fbuy['hand_kw'], fbuy['jieba_kw'])
            buys.append(fbuy)
        return buys


    def save_data(self, filename, data):
        open(filename, 'w', encoding='u8').write(json.dumps(data, ensure_ascii=False))



if __name__ == "__main__":
    es_sell = LoadElasticSearch(index='sell', doc_type='content')
    es_sell.set_config()

    es_buy = LoadElasticSearch(index='buy', doc_type='content')
    es_buy.set_config()

    ext = Extend()

    buys, sells = ext.load_data_from_troop(is_exist=False)

    buys = ext.extend_buy(buys)
    sells = ext.extend_sell(sells)

    es_sell.insert_data(sells,print_result=True)
    es_buy.insert_data(buys,print_result=True)

    ext.save_data('search_sells.json', sells)

    ext.save_data('search_buys.json', buys)
