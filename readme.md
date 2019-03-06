# 步骤 
## 交易信息获取
- Android Accessible Service
- QQ.db root后异或解库

## 数据清洗、关键词提取
- 需求关键字
- 过滤条件

## Query Expansion
- 查询关键词的近义词（Embedding）

## Sell Expansion
- 根据专利号爬取相关文本信息及过滤条件
	- 验证码：用百度或腾讯OCR识别
	- 封IP：ip代理池

## SearchEngine
- 

# 已完成的部分工作
- QQ，微信的聊天记录获取及解码
- 对SooPAT的爬取及验证（无法访问）
- 对sipo的爬取及验证（验证的post页面有问题，有一些没有相亲信息）
- 粗粒度买卖信息的抽取
- 结构化买卖关键词抽取（还要提高专有名词的识别率 / IPC） <- 已升级！姑且还好
- 售卖信息的导入搜索引擎
- 查询(buy)扩展
	- 近义词扩展（近义词词库+word2vec）
	- 
- now！sell信息扩展
	- sell：详情信息的爬取，分词，入库
	- 根据主分类号与IPC对接？
	- IPC主要是 A01B 3/00 部分，再往下过于详细

# 问题
## 总问题
- 结构化怎么提高准确率（语料库？关键词抽取？）
- 一些专利找不到，有些 未缴费/下证 的信息查不到 
- 爬下来的摘要怎么处理？（分词之后，怎么扩展）
 - 搜索引擎部分的优化怎么做？

## 购买关键信息提取
- 中文博大精深
	- 要。。。，不要。。。
	- 要西药的，中成药不要


# 结构化信息抽取
- 条件词（专利状态信息）：授权未缴费（未缴费、未交费、未下证），交费已下证（下证），实用新型专利（实用、新型），发明专利（发明），外观专利
- 附加条件：价格（1.2万），当天全款，数量（8件），不要（不要装置设备）
- 标签词：【】里
- 关键词：。。。相关，。。。方面，。。。方向
- 过滤掉，'代写' in

# 搜索与索引结构设计
## Tabel_buy
- hand_kw (keyword)：手工正则分词
- jieba_kw (keyword)：jieba再分词
- ptype (keyword)：专利类型（发明，实用，外观）
- cond (keyword)：状态（未缴费，下证，不限）
- other (text)：其他条件
- time(date)：（by day）
- contact (keyword)：qq（微信号是字符串）
- 扩展
	- synonym (keyword)：近义词查询扩展，Synonym库   <- 很扯，有点问题（名词还行，动词偏），可能是w2v训练语料的问题

## Table_sell
- id (keyword)：专利号
- title (text-ik)：专利名称
- jieba_kw (keyword)：对专利名的分词预处理	
- ptype (keyword)：专利类型（发明，实用，外观）
- cond (keyword)：状态（未缴费，下证，不限）
- time(date)：date（by day）
- contact (keyword)：qq（微信号是字符串）
- 扩展
	- summary (text-ik)：专利摘要信息
	- sum_key (keyword)：jieba发一下
	- IPC

## Search
- Query多词在Doc多字段索引
- 对sell和buy分开查询
- 对doc内容的扩展（近义词+摘要）
- 对查询的扩展
- 两种匹配方法
	- Terms 精准匹配（手工分词+jieba）
	- Match 文档匹配（手工后去停词当文档）
- BUY
	- 关键词组的精准匹配  <--无法确定中心词，如何保证有序
	- 手工组合后文档的muilt_match
- SELL
	- title，summary的Match
	- jieba_kv，sum_kv的Terms
- 问题
	- 如何对精准匹配在前面的词加权重
	- 在DSL里如何对Fields加权



## 第二阶段大体思路
- 关于如何扩展的问题
- Query还是Doc的扩展
	- 对Doc的索引，多粒度多级，从完整的字符串匹配到分词之后索引
	- 扩展Query（keyword,split,simlar,category）
- 分词的质量有限
	- 相似词的在一般的语料上训练出来不够准确
	- 考虑用专利内容做语料
- IPC的树结构怎么用？怎么建索引
	- 把IPC底层的每一个叶子作为单位与Query做匹配
	- Rank之后取Top20的热词作为扩展
-Match的查准查全提到首位
- 还是传统的搜索引擎的字符串匹配的问题（词袋）
- 总之先把流程串下来

- Other by myself
	- 模型嵌套的端对端的方法 <- 有没有可能会提升？
	- 问答模型？
	- 根据购买记录训练模型（如果有交易信息的话）
	- 可不可以转化为一个推荐的问题（感觉有点偏）
	- 基于内容和主题的方法，从title+desc中提取，映射到同一特征空间 
	- 
 

# 搭建流程
## 数据获取
- Login
	- 用户扫描二维码模拟登录
	- 勾选待爬取专利群号
	- 掉线通知及扫描页面呈现
- 消息截获
	- 在虚拟机上搭建手机QQ模拟器
	- 在Android解码QQ和微信数据库
	- 轮询Sqlite查询近期消息
	- Post到服务器缓存到数据库

## 数据处理
- 过滤交易信息
- 条件信息抽取
	- 专利状态（未缴费、下证）
	- 专利类型（实用，发明，外形）
- 分词提取核心词
	- 手工正则
	- 分词库jieba,xm,fool,
	- 训练自己的NLP的分词任务
- 结构化
	- 去停词后文本
	- 关键词
	- 专利条件信息
	- 联系方式
	- 时间
- 扩展查询
	- extend message
	- 近义词 + 专利摘要
- 入库
	- 不去重全部放入数据库
	- 后台提供增删查改操作
	- 前台向用户展示入库信息
	- 基于SQL过滤+聚集的简易查询

## 数据查询
- Post到ES
- 构造查询，模糊匹配
- 对query扩展
- 设计搜索引擎前端页面
	- 基本的查询
	- 条件查询
	- 查询建议



# 方向
## 现有问题
- 需要一个android开发，帮忙完成微信、登录模块的设计
- 定时唤醒的部分有没有什么问题
- 如何防止过程中的数据丢失，冗余？ t
- 先入库再扩展 <-Now
- SQL需要提供哪些具体的查询服务
- 搜索优化这里感觉还能做很多，能不能给个目标，他怎么查询，展示什么
	来确定查询构造的部分



# 使用说明
## 环境依赖
- python3
	- APScheduler
	- jieba
	- elasticsearch
	- elasticsearch_dsl
	- synonyms
- 代理IP池配置参照 https://github.com/qiyeboy/IPProxyPool

## 使用
- 运行IPProxyPool/IPProxy.py
- 运行虚拟器上QQ，WX，改权限，运行获取APP
 -运行web/mprocess/main.py