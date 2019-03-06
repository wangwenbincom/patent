import json
import random
import sqlite3
from pprint import pprint

import matplotlib.pyplot as plt
import requests
from PIL import Image
from bs4 import BeautifulSoup


class CwralPatent:
    def __init__(self, patent_ids):
        self.patent_ids = patent_ids
        self.conn = sqlite3.connect('data/patent.db')

    def get_proxy(self, types=0, protocol=1):
        data = {'types': types, 'protocol': protocol}
        url = "http://127.0.0.1:8000"
        proxy_list = requests.get(url, data=data).json()
        top = random.choice(sorted(proxy_list, key=lambda x: x[2], reverse=True)[:5])
        return top[0] + ':' + str(top[1])

    def delete_proxy(self, proxy_ip):
        r = requests.get("http://127.0.0.1:8000/delete?ip={}".format(proxy_ip))
        print(r.text)

    def getHtml(self, sess, url, my_proxy=None):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/64.0.3282.186 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate',
        }

        retry_count = 3
        proxy = self.get_proxy(types=1, protocol=1) if my_proxy is None else my_proxy
        print(proxy, url)
        while retry_count > 0:
            try:
                proxys = {"https": "https://{}".format(proxy)}
                response = sess.get(url, proxies=proxys, headers=header, timeout=5)
                return response, proxy
            except Exception:
                retry_count -= 1
        # delete_proxy(proxy.split(':')[0])
        return None

    def postHtml(self, sess, url, data, my_proxy=None):
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/71.0.3578.80 Safari/537.36"
        }
        retry_count = 5
        proxy = self.get_proxy(types=1, protocol=1) if my_proxy is None else my_proxy
        print(proxy, url, data)
        while retry_count > 0:
            try:
                proxys = {"https": "https://{}".format(proxy)}
                response = sess.post(url, proxies=proxys, data=data, headers=header)
                return response, proxy
            except Exception:
                retry_count -= 1
        # delete_proxy(proxy.split(':')[0])
        return None

    def crawl_SooPAT(self, id):
        sess = requests.session()
        url = 'http://www1.soopat.com/Patent/%s' % id
        response, my_proxy = self.getHtml(sess, url)
        print(response)
        response.encoding = 'utf-8'
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        pprint(html)
        title = soup.title.text.translate({ord(k): None for k in '\n\r\t'})

        # if soup.title.text == '错误页面':
        #     return None

        if title == '请输入验证码':
            while (True):
                # img_src = soup.img['src']
                r, proxy = self.getHtml(sess, url='http://www1.soopat.com' + '/Account/ValidateImage',
                                        my_proxy=my_proxy)
                img = r.content
                filename = 'cache_img_soopat.gif'
                with open(filename, 'wb') as wf:
                    wf.write(img)
                image = Image.open(filename).convert("RGB")
                plt.imshow(image)
                plt.show()
                code = input('请输入验证码：')
                vali_page = 'http://www1.soopat.com/Home/RandomCdPost'
                data = {'Cd': code, 'Url': '/Patent/' + id}
                r, my_proxy = self.getHtml(sess, url=vali_page, my_proxy=my_proxy, data=data)
                r.encoding = 'utf-8'
                pprint(r.text)
                soup = BeautifulSoup(r.text)
                # if soup.title.text == '错误页面':
                #     return None
                if soup.title.text == '请输入验证码':
                    continue
                desc = soup.find('div', class_='cp_jsh').get_text()
                return desc[16:-4]

        desc = soup.find('td', class_='sum f14').get_text()
        body = str(soup.find('div', class_='upbox'))
        return desc, body

    def SooPAT(self):
        sell = self.open_sell_dict('../sell.json')
        sell = list(map(lambda id: id[:12], sell))
        with open('checkpoint.txt', 'r') as temp:
            checks = temp.read().split(' ')
        for id in sell:
            if id in checks:
                continue

            description, body = self.crawl_SooPAT(id)
            checks.append(id)

            print(id, description, sep='\n')
            # with open('checkpoint.txt', 'a') as f:
            #     f.write(id + ' ')
            # with open('unprocessed.data', 'a', encoding='utf-8') as up:
            #     up.write(json.dumps({id: body}) + '\n')
            # with open('desc.data', 'a', encoding='utf-8') as desc:
            #     desc.write(json.dumps({id: description}) + '\n')

    def crawl_sipo(self, patent_id):
        sess = requests.session()
        url = 'http://epub.sipo.gov.cn/patentoutline.action'
        strWhere = "AN,DPR,IAN+='{}%' or ABH='{}'".format(patent_id, patent_id)
        data = {"strWhere": strWhere}
        response, my_proxy = self.postHtml(sess, url, data)
        # encoding必须要，否soup之后也无法解析u8
        response.encoding = 'utf-8'
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        # 不是页面返回的cookie，而是图片返回的
        # cookie = response.cookies
        # print(dict(cookie))

        if soup.title.text == '错误页面':
            return None

        if soup.title.text == '请输入验证码':
            while (True):
                img_src = soup.img['src']

                r, proxy = self.getHtml(sess, url='http://epub.sipo.gov.cn' + img_src, my_proxy=my_proxy)
                # cookie = r.cookies
                # print(dict(cookie))
                img = r.content
                filename = 'cache_img.jpg'
                with open(filename, 'wb') as wf:
                    wf.write(img)
                image = Image.open(filename)
                plt.imshow(image)
                plt.show()
                code = input('请输入验证码：')
                vali_page = 'http://epub.sipo.gov.cn/verify-captcha.jpg'
                data = {'response': code}
                r, my_proxy = self.postHtml(sess, url=vali_page, my_proxy=my_proxy, data=data)
                r.encoding = 'utf-8'
                soup = BeautifulSoup(r.text)
                if soup.title.text == '错误页面':
                    return None
                if soup.title.text == '请输入验证码':
                    continue
                desc = soup.find('div', class_='cp_jsh').get_text()
                return desc[16:-4]

        desc = soup.find('div', class_='cp_jsh').get_text()
        return desc[16:-4]

    def sipo(self):
        sell = self.open_sell_dict('../sell.json')
        sell.sort()

        with open('sipo_ckp.txt', 'r') as f:
            checks = json.loads(f.read())

        for i, id in enumerate(sell):
            if id in checks:
                print(id + ' is past')
                continue

            if i % 3 == 0:
                with open('sipo_ckp.txt', 'w') as wf:
                    wf.write(json.dumps(checks))

            print("%s is being processed" % id)
            desc = self.crawl_sipo(id)
            if desc == '':
                print('Just jump this time', id)
                continue
            print(desc)
            with open('sipo_desc.data', 'a', encoding='u8') as sf:
                sf.write(json.dumps({id: desc}, ensure_ascii=False) + '\n')
            checks.append(id)
            # sleep(1)
            # time.sleep(20 + random.randint(-5, 10))

    def crawl_baiten(self, id):

        url = 'https://www.baiten.cn/patent/view.html' \
              '?patid=CN{}&q={}'.format(id[:-1] + '.' + id[-1], id)
        while True:
            sess = requests.session()
            temp = self.getHtml(sess, url)
            if temp != None:
                response, my_proxy = temp
                break

        response.encoding = 'utf-8'
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        pprint(soup.title)

        if soup.title.text == '佰腾网 -  查专利就上佰腾网':
            self.delete_proxy(my_proxy.split(':')[0])
            return None

        # for key in soup.find('ul',class_='keywords').findAll('li'):
        #     print(key.title)
        desc = soup.find('p').get_text()[:-8]
        print('desc:', desc)
        return desc

    def baiten(self):
        sell = self.patent_ids
        sell.sort()
        checkpoint = 'data/ckp.txt'

        patent_summary = dict()

        with open(checkpoint, 'r') as f:
            checks = f.read().split(',')

        for i, id in enumerate(sell):
            if id in checks:
                print(id + ' had been cwraled!')
                continue

            print("%s is being processed" % id)
            desc = self.crawl_baiten(id)
            if desc == None:
                print('Just jump this time', id)
                continue
            print(desc)

            patent_summary[id] = desc
            cursor = self.conn.cursor()
            self.cache_db(cursor, id, desc)
            with open('data/patent_summary.data', 'a', encoding='u8') as sf:
                sf.write(json.dumps({id: desc}, ensure_ascii=False) + '\n')

            checks.append(id)
            with open(checkpoint, 'a', encoding='u8') as ck:
                ck.write(id + ',')

            # sleep(1)
        return patent_summary

    def cache_db(self, cursor, id, smy):
        try:
            sql_insert = "INSERT INTO patent_summary(patent_id,summary) VALUES ('{}','{}')".format(id, smy)
            cursor.execute(sql_insert)
            self.conn.commit()
        except Exception as e:
            print(e)

# if __name__ == "__main__":
#     # SooPAT()
#     # sipo()
#     patent = CwralPatent()
#     patent.baiten()
