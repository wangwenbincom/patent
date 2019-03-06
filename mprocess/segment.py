import json
import re
from itertools import chain

import jieba
from pprint import pprint


class Segment:
    def __init__(self, is_print=False, segm='jieba'):
        self.is_print = is_print
        self.sgem = segm

        self.c_dict = {
            "授权未缴费": "未缴费", "授权": "未缴费", "未缴费": "未缴费", "未交费": "未缴费", "未下证": "未缴费", '缴费': '下证',
            "交费已下证": '下证', '下证': '下证', '状态不限': '不限', '不限': '不限'
        }
        self.t_dict = {
            '实用新型': '实用', '实用': '实用', '新型': '实用', '发明专利': '发明',
            '发明': '发明', '外观专利': '外观', '外观': '外观',
        }

        self.stop_words = set([line.strip() for line in open('data/stopwords.txt', 'r', encoding='u8').readlines()])
        self.cond_dict = [
            "类型不限", '实用新型', '实用', '新型', '发明专利', '发明', '外观专利', '外观',
            "授权未缴费", "授权", "未缴费", "未交费", "缴费", "未下证", "交费已下证", '下证', '状态不限', '不限'
        ]
        self.type_dict = {'实用新型', '实用', '新型', '发明专利', '发明', '外观专利', '外观', '类型不限'}

        self.str_ptype = '|'.join(["授权未缴费", "授权", "未缴费", "未交费", "缴费", "未下证", "交费已下证", '下证', '状态不限', '不限'])
        self.str_cond = '|'.join(['实用新型', '实用', '新型', '发明专利', '发明', '外观专利', '外观'])
        self.str_tag = ['【(.*?)】', '（(.*?)）', '[(.*?)]']
        self.str_other = '|'.join(['不要[\u4e00-\u9fa5]*', '要[\u4e00-\u9fa5]*', '\d{2,}年[\u4e00-\u9fa5]', '[0-9].[0-9]+万',
                                   '当天全款', '[0-9]+件', '批量', '截止日', '未变更过权利人', '带价格'])

        self.re_id = re.compile('[0-9]{9,}')
        self.re_ptype = re.compile(self.str_ptype)
        self.re_cond = re.compile(self.str_cond)
        self.re_other = re.compile(self.str_other)

        self.re_sub = re.compile("\n|\.|求购|也行|反正|做|[0-9A-Za-z]|发|给|来|谢谢|合适|用于|急|几个|符合|需|证书|主要|我|'|\]|\["
                                 '|只|最好|一种|。|状态|均可|那种|这|！|不限|关键词|关键字|个|本身|可以|领域|申请|办登|截止|日期|期')
        self.re_split = re.compile('方面|相关|和|跟|方法|类|的|，|：|:|或者|比如|如|也|或|·|、|;|；|用于|方向|具有'
                                   '| |,|关于|等|就是|是|都|【|】|（|）|\(|\)|专利|有关|—|有|技术|之|这些|一定|/')

        self.re_best_in = re.compile('相关|类|、|方面|领域|\.|方法|一种|，')
        self.re_best_not = re.compile('www|欢迎|表情|代写|反感|私聊|\d{12}')

        self.self_dict = set(json.loads(open('data/ipc_words.json', 'r', encoding='u8').read()))

        for word in self.self_dict:
            jieba.add_word(word)

    def prcess_one_sblock(self, name, time, line, items):
        cond = list(set(re.findall('|'.join(self.cond_dict), line)))
        sell_info = []
        for item in items:
            iid = re.findall('\d{12}.', item.replace('.', ''))[0]
            cline = re.sub(
                self.str_ptype + '|' + self.str_cond + '|' + '【(.*?)】|（(.*?)）|[(.*?)]' + '|' + self.str_other,
                '', item)
            cline = re.sub(self.re_sub, '', cline + ',')
            hand = [x for x in re.split(self.re_split, cline) if x != '']
            sell = [iid, str(name), time, cond, ' '.join(hand)]
            sell_info.append(sell)
            # print(item,' '.join(hand),fmt_sell['title'],sep='\n')
        return sell_info

    def get_sell(self, blocks):
        sell = list()
        for block in blocks:
            # print('\n' + '+++' * 40)
            # print('block:')
            # pprint(block)

            user_id, time, toline = block
            block = block[2].split('\n')

            cond = list(filter(lambda line: re.findall('实用新型|实用|发明|外观|下证专利', line) != [], block))
            items = list(filter(lambda line: re.findall('[0-9]{12}X|[0-9]{13}', line) != [], block))

            print(user_id, time) if self.is_print else None
            if len(items) == 0:
                continue
            print('cond:', cond) if self.is_print else None
            if len(cond) == 1:
                sell_info = self.prcess_one_sblock(user_id, time, toline, items)
                sell += sell_info
                continue
            if len(cond) > 1:
                old = 0
                for i, line in enumerate(block):
                    if line in cond or i == len(block) - 1:
                        small_block = block[old:i]
                        # if self.is_print:
                        # print('\n' + '+++' * 40)
                        # print('small_block:')
                        # pprint(small_block)

                        line_ = ''.join(small_block)
                        # cond_ = re.findall('实用新型|实用|发明|外观|下证专利', line_)
                        items_ = list(filter(lambda line: re.findall('[0-9]{12,13}', line_) != [], small_block))
                        if len(items_) > 0:
                            sell_info = self.prcess_one_sblock(user_id, time, line, items)
                            sell += sell_info
                        old = i
        return sell

    def not_noise(self, line):
        flag1 = flag2 = True

        if self.re_id.findall(line) != []:
            flag1 = flag2 = False
        if line == '\n':
            flag1 = flag2 = False
        if self.re_best_not.findall(line) != []:
            flag1 = False
        if self.re_best_in.findall(line) == []:
            flag2 = False
            if re.findall('发明|实用|状态|新型|未|下证| {4}]',line) != []:
                flag2 = True
        print(line) if not (flag1 and flag2) else None
        return (flag1 and flag2)

    def result_test(self, line):

        # 原样输出
        raw = line.strip()
        print("\nRAW:", line.strip()) if self.is_print else None

        # 过滤(OK:标点符号的分割不影响分词)
        table = {ord(key): None for key in '\t\n'}
        cline = line.translate(table)

        # 提取
        tag = list(chain(*[re.findall(r_tag, line) for r_tag in self.str_tag]))
        ptype = re.findall(self.re_ptype, line)
        cond = re.findall(self.re_cond, line)
        other = re.findall(self.re_other, line)

        # check in line
        if len(ptype) == 0 and len(cond) == 0:
            if re.findall('方法|相关|领域|方向|方面|专利|、|工艺|装置', line) == []:
                return None

        cline = re.sub(self.str_ptype + '|' + self.str_cond + '|' + '【(.*?)】|（(.*?)）|[(.*?)]' + '|' + self.str_other,
                       '', cline)
        cline = re.sub(self.re_sub, '', cline + ',' + ' '.join(tag))
        hand = [x for x in re.split(self.re_split, cline) if x != '']

        jie_cut = jieba.lcut('/'.join(hand))
        jie_cut = sorted(list(set(jie_cut) - self.stop_words), key=jie_cut.index)

        if self.is_print:
            print("ptype{}\ncond{}\nother{}".format(ptype, cond, other))
            print("手工:", set(hand))
            print("去停词:", jie_cut)

        return raw, ptype, cond, other, hand, jie_cut

    def get_buy(self, blocks):
        buy = []
        for block in blocks:
            user_id, time, content = block
            block = content.split('\n')
            for i, line in enumerate(block):
                if '求购' in line:
                    small_block = block[i:]
                    for line in small_block:
                        if self.not_noise(line):
                            result = self.result_test(line)
                            if result != None:
                                a_buy = [user_id, time] + list(result)
                                buy.append(a_buy)
                    break
        return buy

    # def data_processing(self, lines):
    #     block_start = set(list(filter(lambda x: x[:5] == '2019-', lines)))
    #     table = {ord(key): None for key in u"\xa0\u2665"}
    #     lines = [line.translate(table) for line in lines]
    #     blocks = self.split_block(lines, block_start)
    #
    #     sell = self.get_sell(blocks)
    #     buy = self.get_buy(blocks)
    #     return sell, buy
    #
    # def split_block(self, lines, block_start):
    #     blocks = []
    #     old = 0
    #     for i, line in enumerate(lines):
    #         if line in block_start:
    #             block = lines[old:i]
    #             time_name = lines[old].split(' ', maxsplit=2)
    #             # print(time_name)
    #             block = time_name + block
    #             blocks.append(block)
    #             old = i
    #     blocks.pop(0)
    #     return blocks

    # save

# if __name__ == '__main__':
#     proc = Segment(is_print=False)
#     row_dir = 'raw_data/'
#     sells = []
#     buys = []
#     files = os.listdir(row_dir)
#     for filename in files:
#         lines = open(row_dir + filename, 'r', encoding='utf-8').readlines()
#         sell, buy = proc.data_processing(lines)
#         sells += sell
#         buys += buy
#
#     sells, buys = proc.distinct_data(sells, buys)
#     proc.save_data('all_buys.json', buys)
#     proc.save_data('all_sells.json', sells)
#     print(len(sells))
#     print(len(buys))

# proc.push_database_buys(buys)
# proc.push_database_sells(sells)
