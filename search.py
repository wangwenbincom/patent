from pprint import pprint

import jieba
from elasticsearch_dsl import connections, Search, Q


class PatentSearch:
    def __init__(self, host, port):
        connections.create_connection(host=host, port=port)
        self.c_dict = {
            "授权未缴费": "未缴费", "授权": "未缴费", "未缴费": "未缴费", "未交费": "未缴费", "未下证": "未缴费", '缴费': '下证',
            "交费已下证": '下证', '下证': '下证', '状态不限': '不限', '不限': '不限'
        }
        self.pt_dict = {
            '实用新型': '实用', '实用': '实用', '新型': '实用', '发明专利': '发明',
            '发明': '发明', '外观专利': '外观', '外观': '外观', '类型不限': '类型不限'
        }

    def extend_sell_query(self, query):
        ex_query = []
        return ex_query

    def search_sell(self, query, ptype, cond):
        s = Search(index='sell')

        if ptype != '':
            s = s.filter('match', ptype=self.pt_dict[ptype])
        if cond != '':
            s = s.filter('match', cond=self.c_dict[cond])

        # s = s.source(['title','jieba_kw','summary','ptype','cond'])

        q = Q('multi_match', query=' '.join(query), fields=['title^3', 'summary']) | \
            Q("terms", jieba_kw=query) | \
            Q("terms", sum_key=query)


        s = s.query(q)
        pprint(s.to_dict())
        r = s.execute()
        return r

    def search_buy(self, query, ptype, cond):
        s = Search(index='buy')

        if ptype != '':
            s = s.filter('match', ptype=self.pt_dict[ptype])
        if cond != '':
            s = s.filter('match', cond=self.c_dict[cond])

        # s = s.source(['hand_kw', 'jieba_kw', 'synonym', 'ptype', 'cond'])

        q = Q("bool", should=[Q("terms", hand_kw=query),
                              Q("terms", jieba_kw=query),
                              Q("terms", synonym=query),
                              Q("match", raw=' '.join(query))])

        # q = Q('multi_match', query=' '.join(query), fields=['raw']) | \
        #     Q("terms", hand_kw=query) | \
        #     Q("terms", jieba_kw=query) | \
        #     Q("terms", synonym=query)


        s = s.query(q)
        pprint(s.to_dict())
        r = s.execute()
        return r

    def test_buy(self, query):
        query = jieba.lcut_for_search(query)
        ptype = ''
        cond = ''
        r = ps.search_buy(query=query, ptype=ptype, cond=cond)
        pprint([hit.to_dict() for hit in r])

    def test_sell(self, query):
        query = jieba.lcut_for_search(query)
        ptype = ''
        cond = ''
        r = ps.search_sell(query=query, ptype=ptype, cond=cond)
        pprint([hit.to_dict() for hit in r])


if __name__ == '__main__':
    ps = PatentSearch('localhost', 9200)
    flag = input('Is Buy?')
    while (True):
        query = input()
        ps.test_buy(query) if flag == 1 else ps.test_sell(query)

    # query = ['新能源','汽车']
    # ptype = ''
    # cond = ''
    # # ptype,cond = None,None
    # r = ps.search_sell(query=query,ptype=ptype,cond=cond)
    # pprint([hit.to_dict() for hit in r])
