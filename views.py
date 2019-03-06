from datetime import datetime
from pprint import pprint

import jieba
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

from forms import *
from search import PatentSearch

config = {
    # 'secret_key': '000123',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///mprocess/data/patent.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': True
}

app = Flask(__name__)
app.secret_key = '000123'
for key in config.keys():
    app.config[key] = config[key]
db = SQLAlchemy(app)
ps = PatentSearch('localhost', 9200)


@app.route('/', methods=["GET"])
def index():
    db.create_all()
    return render_template('index.html')

def history_record(query):
    with open('history.txt','a',encoding='u8',errors='ignore') as wf:
        wf.write(query+',')

@app.route('/search', methods=["POST", "GET"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        pprint(form.data)
        history_record(form.query.data)

        if form.trade.data == 'buy':
            is_buy = True
            query = jieba.lcut_for_search(form.query.data)
            ptype = form.ptype.data
            cond = form.cond.data
            r = ps.search_buy(query=query, ptype=ptype, cond=cond)
            results = [hit.to_dict() for hit in r]
            return render_template("SearchResult.html", results=results, is_buy=is_buy)

        if form.trade.data == 'sell':
            is_buy = False
            query = jieba.lcut_for_search(form.query.data)
            ptype = form.ptype.data
            cond = form.cond.data
            r = ps.search_sell(query=query, ptype=ptype, cond=cond)
            results = [hit.to_dict() for hit in r]
            return render_template("SearchResult.html", results=results, is_buy=is_buy)

    return render_template('search.html', form=form)


@app.route('/SimpleSearch', methods=["POST", "GET"])
def simple_search():
    form = SqlForm()

    if form.validate_on_submit():
        pprint(form.data)

        if form.trade.data == 'buy':
            is_buy = True
            keyword = form.keyword.data
            ptype = form.ptype.data
            cond = form.cond.data
            time = form.time.data
            cotact = form.contact.data
            buys = Buy.query.filter(db.and_(
                Buy.hand_kw.like('%{}%'.format(keyword)),
                Buy.ptype.like('%{}%'.format(ptype)),
                Buy.cond.like('%{}%'.format(cond)),
                Buy.time.like('%{}%'.format(time)),
                Buy.contact.like('%{}%'.format(cotact))
            )).all()
            print(buys)
            return render_template('SimpleResult.html', results=buys, is_buy=is_buy)

        if form.trade.data == 'sell':
            is_buy = False
            pid = form.pid.data
            keyword = form.keyword.data
            ptype = form.ptype.data
            cond = form.cond.data
            time = form.time.data
            cotact = form.contact.data
            sells = Sell.query.filter(db.and_(
                Sell.pid.like('%{}%'.format(pid)),
                Sell.title.like('%{}%'.format(keyword)),
                Sell.ptype.like('%{}%'.format(ptype)),
                Sell.cond.like('%{}%'.format(cond)),
                Sell.time.like('%{}%'.format(time)),
                Sell.contact.like('%{}%'.format(cotact))
            )).all()

            return render_template('SimpleResult.html', results=sells, is_buy=is_buy)

    return render_template('SimpleSearch.html', form=form)


# def process_search(data):
#     if data['ptype']


@app.route('/getQQMsg', methods=["POST", "GET"])
def getQQMsg():
    if request.method == 'POST':
        data = request.json
        if data != []:
            for qq_msg in data:
                try:
                    db.session.add(Cache(*qq_msg))
                    db.session.commit()
                    db.session.add(RawData_QQ(*qq_msg))
                    db.session.commit()
                except Exception as e:
                    print(e)
                    db.session.rollback()

    return 'Get DAZE!!!'


@app.route('/getWXMsg', methods=["POST", "GET"])
def getWXMsg():
    if request.method == 'POST':
        data = request.json

        if data != []:
            for wx_msg in data:
                try:
                    db.session.add(Cache(*wx_msg))
                    db.session.add(RawData_WX(*wx_msg))
                    db.session.commit()
                except Exception as e:
                    print(wx_msg[0], datetime.fromtimestamp(int(wx_msg[1])))
                    print(e)
                    db.session.rollback()

    return 'Get DAZE!!!'


@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(form.data)
        user = User.query.filterby(username=form.username, password=form.password).first()
        print("user:", user)
        if user != []:
            return 'sadas'
            # return url_for('main')

    return render_template('login.html', form=form)


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        pass
    return render_template('register.html', form=form)


@app.route('/logout', methods=["GET"])
def logout():
    return 'OUT'


class RawData_QQ(db.Model):
    __tablename__ = 'rawdata_3537838886'
    id = db.Column(db.Integer, primary_key=True)
    stime = db.Column(db.Integer)
    user_id = db.Column(db.Text)
    content = db.Column(db.Text)

    def __init__(self, id, stime, user_id, content):
        self.id = id
        self.stime = stime
        self.user_id = user_id
        self.content = content


class RawData_WX(db.Model):
    __tablename__ = 'rawdata_plunder'
    id = db.Column(db.Integer, primary_key=True)
    stime = db.Column(db.Integer)
    user_id = db.Column(db.Text)
    content = db.Column(db.Text)

    def __init__(self, id, stime, user_id, content):
        self.id = id
        self.stime = stime
        self.user_id = user_id
        self.content = content

class Cache(db.Model):
    __tablename__ = 'cache'
    id = db.Column(db.Integer, primary_key=True)
    stime = db.Column(db.Integer)
    user_id = db.Column(db.Text)
    content = db.Column(db.Text)

    def __init__(self, id, stime, user_id, content):
        self.id = id
        self.stime = stime
        self.user_id = user_id
        self.content = content


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return 'User {}'.format(self.username)


class Buy(db.Model):
    __tablename__ = 'ext_buys'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    raw = db.Column(db.Text)
    hand_kw = db.Column(db.Text)
    jieba_kw = db.Column(db.Text)
    ptype = db.Column(db.Text)
    cond = db.Column(db.Text)
    other = db.Column(db.Text)
    time = db.Column(db.Text)
    contact = db.Column(db.Text)
    synonym = db.Column(db.Text)


class Sell(db.Model):
    __tablename__ = 'ext_sells'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pid = db.Column(db.Text)
    title = db.Column(db.Text)
    jieba_kw = db.Column(db.Text)
    ptype = db.Column(db.Text)
    cond = db.Column(db.Text)
    time = db.Column(db.Text)
    contact = db.Column(db.Text)
    summary = db.Column(db.Text)
    sum_key = db.Column(db.Text)


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5050)
    app.run(host='0.0.0.0', port=5050, debug=True)
