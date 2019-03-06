import re
from itertools import chain

import jieba


class Structured:
    def __init__(self):
        self.c_dict = {
            "授权未缴费": "未缴费", "授权": "未缴费", "未缴费": "未缴费", "未交费": "未缴费", "未下证": "未缴费", '缴费': '下证',
            "交费已下证": '下证', '下证': '下证', '状态不限': '不限', '不限': '不限'
        }
        self.t_dict = {
            '实用新型': '实用', '实用': '实用', '新型': '实用', '发明专利': '发明',
            '发明': '发明', '外观专利': '外观', '外观': '外观', "类型不限": "类型不限"
        }
        self.stop_words = set([line.strip() for line in open('data/stopwords.txt', 'r', encoding='u8').readlines()])
        self.num2type = {'1': '发明', '2': '实用', '3': '外观'}

    def format_sells(self, sell_data):
        fmt_sells = list()
        flag_set = set()
        print(sell_data)
        for sell in sorted(sell_data,reverse=True,key=sell_data.index):
            id_, user_, time_, cond_, item_ = sell
            flag = id_+user_
            if flag in flag_set:
                print(flag)
                continue
            else:
                flag_set.add(flag)
            li_tag = ['【(.*?)】', '（(.*?)）', '[(.*?)]']
            a_sell = {}
            a_sell['pid'] = id_
            a_sell['title'] = re.sub('\d{12}.' + '|' + '|'.join(li_tag), '', item_).translate(
                {ord(k): None for k in ' \n\t【】（）\(\)'})
            a_sell['jieba_kw'] = list(set(jieba.lcut(a_sell['title'])) - self.stop_words) + \
                                 list(chain(*[re.findall(r_tag, item_) for r_tag in li_tag]))
            # a_sell['ptype'] = ''.join(list(set([self.t_dict[typ] for typ in cond_ if typ in set(self.t_dict.keys())])))
            a_sell['ptype'] = self.num2type[id_[4]] if id_[4] in self.num2type.keys() else '其他'
            a_sell['cond'] = ''.join(list(set(
                [self.c_dict[cond] for cond in cond_ if cond in set(self.c_dict.keys())])))
            a_sell['time'] = time_
            a_sell['contact'] = user_
            # a_sell['summary'] = summary_dict[re.findall('\d{12}.', item_.replace('.', ''))]
            # a_sell['sum_key'] = list(set(jieba.lcut(a_sell['summary']) - stop_words))
            fmt_sells.append(a_sell)
        return fmt_sells

    def format_buys(self, buy_data):
        fmt_buys = list()
        for buy in buy_data:
            user_, time_, raw_, cond_, ptype_, other_, hand_, jie_cut_ = buy
            a_buy = {}
            a_buy['raw'] = raw_
            a_buy['hand_kw'] = hand_
            a_buy['jieba_kw'] = jie_cut_
            a_buy['ptype'] = ''.join(list(set([self.t_dict[typ] for typ in ptype_ if typ in set(self.t_dict.keys())])))
            a_buy['cond'] = ''.join(list(set([self.c_dict[cond] for cond in cond_ if cond in set(self.c_dict.keys())])))
            a_buy['other'] = other_
            a_buy['time'] = time_
            a_buy['contact'] = user_
            fmt_buys.append(a_buy)
        return fmt_buys

    def distinct_data(self, sells, buys):
        sell_ids = set()
        dstc_sell = list()
        for sell in sells:
            id = sell['pid'] + sell['contact']
            if id in sell_ids:
                continue
            else:
                sell_ids.add(id)
                dstc_sell.append(sell)

        buy_ids = set()
        dstc_buy = list()
        for buy in buys:
            try:
                uni = str(buy['contact']) + buy['hand_kw'][0] + buy['hand_kw'][-1]
            except:
                uni = str(buy['contact'])
            print('UNIQUE', uni)
            if uni in buy_ids:
                continue
            else:
                buy_ids.add(uni)
                dstc_buy.append(buy)

        print(len(list(sell_ids)))
        print(len(list(buy_ids)))
        return dstc_sell, dstc_buy
