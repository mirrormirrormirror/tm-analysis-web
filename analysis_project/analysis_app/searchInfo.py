# coding:utf-8
import re
from pymongo import MongoClient
import operator
from snownlp import SnowNLP
import numpy as np
import json
# from analysis_app.function import *
from multiprocessing.dummy import Pool as ThreadPool
from bs4 import BeautifulSoup
from collections import Counter
import pymongo
import urllib.request as ur
from selenium import webdriver
import re
import jieba


class SearchServer:
    def shopImage(self, shopUrl):
        self.driver.get('https:' + shopUrl)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        try:
            return 'https:' + soup.select('div[class="banner-box"] img')[0].attrs['src']
        except:
            return 'https:' + re.findall('url\((.*?)\)', str(soup.select('div[class="main"] a')[0]))[0]

    def itemImage(self, itemId):
        url = 'https://detail.tmall.com/item.htm?id=' + itemId
        html = ur.urlopen(url).read().decode('gbk')
        return re.findall('<title>(.*?)<\/title>', html)[0], 'http://' + re.findall('src=\"\/\/(.*?.jpg)\"', html)[0]

    def __init__(self):
        conn = MongoClient(host="2ja0213922.imwork.net", port=35191)
        db = conn.tmdb
        self.driver = webdriver.PhantomJS()
        self.comment = db.comment
        self.stopword = open('analysis_app\stopword.txt', 'r').read().split('\n')
        self.SDcombine = db.SDcombine
        self.brandGroup = db.brandDateGroup
        self.shopGroup = db.shopDateGroup
        self.combineSet = db.SDcombineSet
        self.dictColumn = {'price_range': 'price', 'sales_range': 'monthSales', 'collect_range': 'collectNum',
                           'stock_range': 'totalQuantity', 'brand': 'brandName', 'itemId': 'itemId',
                           'shopUrl': 'shopUrl'}
        self.API_name = None  # 请求的API名称
        self.paramList = None  # 参数列表
        self.query = None  # 查询语句
        self.reqColumns = None  # 返回的字段
        self.page = None  # 请求的页数
        self.skip = None
        self.limit = None  # 每页的条数
        self.collect = None  # 请求的表
        self.url = None  # 请求的URL
        self.data = []
        self.newCommentList = []
        self.weekDict = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.city = eval(open('analysis_app\全国城市.txt').read())

    def createQuery(self):
        '''构造查询语句'''
        self.query = {'$and': []}
        for i in self.paramList:
            if ('range' in i[0]):
                split = [float(x) for x in i[1].split('%2C')]
                self.query['$and'].append({self.dictColumn[i[0]]: {'$gt': split[0]}})
                self.query['$and'].append({self.dictColumn[i[0]]: {'$lt': split[1]}})
                continue
            if (i[0] == 'start_date'):
                if (i[1] == '0'):
                    continue
                else:
                    tempDate = i[1][:1] + '.' + i[1][1:]
                    self.query['$and'].append({'updatetime': {'$gt': tempDate}})
            if (i[0] == 'end_date'):
                if (i[1] == '-1'):
                    continue
                else:
                    tempDate = i[1][:1] + '.' + i[1][1:]
                    self.query['$and'].append({'updatetime': {'$lt': tempDate}})
            if (i[0] == 'limit'):
                self.limit = int(i[1])
                continue
            if (i[0] == 'offset'):
                self.offset = i[1]
                self.page = int(int(self.offset) / int(self.limit))
                self.skip = self.page * self.limit
                continue

    def paserUrl(self):
        '''解析url中的参数'''
        self.API_name = re.findall('.*?data\/(.*?)\?', self.url)[0].replace('/', '_')
        self.paramList = re.findall('(\w+)=(.*?)(?=[|&])', re.sub('.*?data\/\?', '', self.url))  # 提取后面参数
        self.createQuery()

    def paserParam(self, method, value):
        self.paramList = value.split('=')
        exec('self.' + method + '()')

    def getData(self):
        '''mongo请求数据'''
        return [x for x in
                self.collect.find(self.query, self.reqColumns).skip(self.skip).limit(self.limit)], self.collect.find(
            self.query, self.reqColumns).count()

    def start(self, url=None, method=None, param=None):
        if (param != None):
            self.paserParam(method=method, value=param)
            return self.data
        else:
            self.url = url
            self.paserUrl()
            exec('self.' + self.API_name + '()')
            data, total = self.getData()
            return {'total': total, 'rows': data}

    def item_itemInfo(self):
        '''请求商品的基本数据'''
        self.reqColumns = {"itemId": 1, "title": 1, "price": 1, "collectNum": 1, "totalQuantity": 1, "monthSales": 1,
                           "_id": 0}
        self.collect = self.SDcombine

    def shop_shopInfo(self):
        '''根据前端条件获取后端店铺相关的信息'''
        self.reqColumns = {'shopName': 1, 'shopUrl': 1, 'monthSales': 1, 'totalQuantity': 1, 'collectNum': 1, '_id': 0}
        self.collect = self.shopGroup

    def brand_brandInfo(self):
        '''根据前端条件筛选出品牌相关的基本数据'''
        self.reqColumns = {"brandName": 1, "collectNum": 1, "totalQuantity": 1, "monthSales": 1, "_id": 0}
        self.collect = self.brandGroup

    def itemDetail(self):
        '''根据id获取商品详细信息如规格等'''
        self.reqColumns = {"destailsDict": 1, "_id": 0}
        self.collect = self.combineSet
        self.query = {self.dictColumn[self.paramList[0]]: self.paramList[1]}
        self.data = [x for x in self.collect.find(self.query, self.reqColumns)]

    def itemSource(self):
        '''根据商品id得出所有搜索关键词所占的比重'''
        self.collect = self.SDcombine
        temp = [x.values() for x in self.collect.aggregate([{"$match": {"itemId": self.paramList[1]}},
                                                            {"$group": {"_id": "$keyWord", "num": {"$sum": 1}}},
                                                            {"$sort": {'num': -1}}])]
        temp = [list(x) for x in temp]
        valueSum = sum([float(x[1]) for x in temp])  # 求和
        top5 = temp[:5]
        self.data = [{x[0]: round(x[1] / valueSum, 3)} for x in top5] + [
            {'其他': sum([float(x[1]) for x in temp[5:]]) / valueSum}]

    def itemTrend(self):
        '''根据id返回某个商品的一周评论数，情感指数，销量的变化数据'''
        '''缺少了情感指数'''
        self.collect = self.SDcombine
        temp = [x for x in self.collect.aggregate([{"$match": {"itemId": self.paramList[1]}},
                                                   {"$project": {"monthSales": 1, "commentsNum": 1, "date": 1,
                                                                 "_id": 0}},
                                                   {"$group": {"_id": "$date",
                                                               "commentsNumSum": {"$max": "$commentsNum"},
                                                               "monthSalesSum": {"$max": "$monthSales"}}},
                                                   {"$sort": {"monthSalesSum": -1}}])]
        if (len(temp) >= 7):
            temp = temp[:7]
        monthSalesList = [round(x['monthSalesSum']) for x in temp]
        monthSalesList.reverse()
        commentsNumList = [round(x['commentsNumSum']) for x in temp]
        commentsNumList.reverse()
        self.data = {"salesTrend": [monthSalesList[x] for x in range(len(monthSalesList))],
                     "commentNumTrend": [commentsNumList[x] for x in range(len(commentsNumList))]}

    def itemCiYun(self):
        '''根据商品id获取某个商品一月的评论词云图数据'''
        self.collect = self.comment
        data = []
        if (len([x for x in
                 self.collect.aggregate([{"$match": {"itemId": self.paramList[1]}}, {"$project": {"_id": 1}}])]) < 50):
            '''如果评论数小于50则实时爬取 "540268867640"'''
            itemId, sellerId = [x for x in self.SDcombine.aggregate(
                [{"$match": {"itemId": self.paramList[1]}}, {"$project": {"_id": 0, "sellerId": 1, 'itemId': 1}}])][
                0].values()
            self.itemComment(itemId, sellerId)
            data = self.newCommentList
        else:
            data = [x['commentContent'] for x in self.collect.aggregate(
                [{"$match": {"itemId": self.paramList[1]}}, {"$project": {"commentContent": 1, "_id": 0}}]) if
                    x['commentContent'] != '']
        b = [j for i in data for j in self.split_jieba(i)]
        di = dict(Counter(b));
        # del di[' ']
        self.data = sorted(di.items(), key=lambda d: d[1], reverse=True)[:50]

    def itemSimilarity(self):
        '''根据商品id和相似类别获取相似商品的数据'''
        pass

    def brandTrend(self):
        '''根据品牌名称获取品牌的销量，评论，情感变化的一周趋势'''
        self.collect = self.brandGroup
        temp = [x for x in self.collect.find({"brandName": self.paramList[1]}).sort([('date', pymongo.DESCENDING)])]
        if (len(temp) >= 7):
            temp = temp[:7]
        monthSalesList = [round(x['monthSales']) for x in temp];
        monthSalesList.sort()
        commentsNumList = [round(x['commentsNum']) for x in temp];
        commentsNumList.sort()
        self.data = {"salesTrend": [monthSalesList[x] for x in range(len(monthSalesList))],
                     "commentNumTrend": [commentsNumList[x] for x in
                                         range(len(commentsNumList))]}

    def brandSource(self):
        '''根据品牌名称获取搜索关键词来源相关数据'''
        self.collect = self.SDcombine
        temp = [x.values() for x in self.collect.aggregate([{"$match": {"brand": self.paramList[1]}},
                                                            {"$group": {"_id": "$keyWord", "num": {"$sum": 1}}},
                                                            {"$sort": {'num': -1}}])]

        temp = [list(x) for x in temp]
        valueSum = sum([float(x[1]) for x in temp])  # 求和
        top5 = temp[:5]
        self.data = [{x[0]: round(x[1] / valueSum, 3)} for x in top5] + [
            {'其他': sum([float(x[1]) for x in temp[5:]]) / valueSum}]  # 求百分比，保留3位小数的结果

    def brandSearchDisplay(self):
        '''根据品牌名称获取商品一周搜索展现数据'''
        self.collect = self.SDcombine
        temp = [x.values() for x in
                self.collect.aggregate([{"$match": {"brand": self.paramList[1]}}, {"$project": {"date": 1, "_id": 0}},
                                        {"$group": {"_id": "$date", "sum": {"$sum": 1}}}, {"$sort": {"_id": -1}}])]
        if (len(temp) >= 7):
            temp = temp[:7]

        temp = [list(x) for x in temp]
        daysSum = [round(x[1]) for x in temp];
        daysSum.reverse()
        self.data = [daysSum[x] for x in range(len(daysSum))]

    def brandTopShop(self):
        self.collect = self.SDcombine
        temp = [x for x in self.collect.aggregate(
            [{"$match": {"brand": self.paramList[1]}}, {"$project": {"shopName": 1, "shopUrl": 1, "_id": 0}}
                , {"$group": {"_id": "$shopName", "sum": {"$sum": 1}, "shopUrl": {"$push": "$shopUrl"}}}
                , {"$project": {"_id": 1, "sum": 1, "shopUrl": {"$slice": ["$shopUrl", -1, 1]}}}
                , {"$sort": {"sum": -1}}
             ])][:5]
        self.data = [(x['_id'], 'https:' + x['shopUrl'][0], x['sum']) for x in temp]

    def brandTopItem(self):
        '''根据品牌名称获取品牌相关产品前五的商品数据'''
        self.collect = self.SDcombine
        temp = [x for x in self.collect.aggregate(
            [{"$match": {"brand": self.paramList[1]}},
             {"$project": {"itemId": 1, "title": 1, "_id": 0}},
             {"$group": {"_id": "$itemId", "title": {"$push": "$title"}, "sum": {"$sum": 1}}}, {"$sort": {"sum": -1}},
             {"$project": {"_id": 1, "sum": 1, "shopUrl": {"$slice": ["$title", -1, 1]}}}
             ])][:5]
        self.data = [['https://detail.tmall.com/item.htm?id=' + x['_id'], x['sum'], x['shopUrl'][0]] for x in temp]

    def brandShopArea(self):
        '''根据品牌名称获取品牌相关店铺的地区分布的数据'''
        self.collect = self.SDcombine
        temp = [x for x in self.collect.aggregate([
            {"$match": {"brand": self.paramList[1]}},
            {"$project": {"deliveryAddress": 1, "shopName": 1, "_id": 0}},
            {"$group": {"_id": "$deliveryAddress", "sum": {"$sum": 1}}},
            {"$sort": {"sum": -1}}
        ])]
        data = []
        for i in temp:
            citySum = [(x, i['sum']) for x in jieba.cut(i['_id']) if x in self.city]
            if (citySum == []):
                continue
            else:
                data.append(citySum[0])
        d = {}
        for i in data:
            if (i[0] not in d):
                d[i[0]] = i[1]
            else:
                d[i[0]] += i[1]
        self.data = [[x, y * 500] for x, y in
                     zip(d.keys(), self.min_max_range(list(d.values()), range_values=(0, 1)))]

    def shopSource(self):
        '''根据店铺url获取店铺的搜索关键词来源'''
        self.collect = self.SDcombine
        temp = [x for x in self.collect.aggregate(
            [{"$match": {"shopUrl": self.paramList[1]}}, {"$project": {"keyWord": 1, "_id": 0}},
             {"$group": {"_id": "$keyWord", "sum": {"$sum": 1}}}, {"$sort": {"sum": -1}}])]
        valueSum = sum([float(x['sum']) for x in temp])  # 求和
        if (len(temp) <= 5):
            self.data = [{x['_id']: round(x['sum'] / valueSum, 3)} for x in temp]
        else:
            top5 = temp[:5]
            print(temp)
            self.data = [{x['_id']: round(x['sum'] / valueSum, 3)} for x in top5] + [
                {'其他': sum([float(x['sum']) for x in temp[5:]]) / valueSum}]

    def shopTrend(self):
        '''根据店铺url获取店铺的产品销量、情感指数、评论数的一周趋势'''
        self.collect = self.SDcombine
        temp = [x for x in self.collect.aggregate([{"$match": {"shopUrl": self.paramList[1]}}, {
            "$project": {"monthSales": 1, "commentsNum": 1, "date": 1, "_id": 0}},
                                                   {"$group": {"_id": "$date", "monthSales": {"$sum": "$monthSales"},
                                                               "commentsNum": {"$sum": "$commentsNum"}}},
                                                   {"$sort": {"_id": -1}}])]
        if (len(temp) >= 7):
            temp = temp[:7]
        monthSalesList = [round(x['monthSales']) for x in temp];
        monthSalesList.reverse()
        commentsNumList = [round(x['commentsNum']) for x in temp];
        commentsNumList.reverse()
        self.data = {"salesTrend": [monthSalesList[x] for x in range(len(monthSalesList))],
                     "commentNumTrend": [commentsNumList[x] for x in
                                         range(len(commentsNumList))]}

    def shopSearchDisplay(self):
        '''根据店铺url获取店铺一周在搜索页的曝光程度趋势'''
        self.collect = self.SDcombine
        temp = [x for x in
                self.collect.aggregate([{"$match": {"shopUrl": self.paramList[1]}}, {"$project": {"date": 1, "_id": 0}},
                                        {"$group": {"_id": "$date", "sum": {"$sum": 1}}}, {"$sort": {"_id": -1}}])]
        if (len(temp) >= 7):
            temp = temp[:7]
        daysSum = [round(x['sum']) for x in temp];
        daysSum.reverse()
        self.data = [daysSum[x] for x in range(len(daysSum))]

    def split_jieba(self, seq):
        return [x for x in jieba.cut(seq) if x not in self.stopword]

    def getBrandData(self, param, value, time):
        return [x['commentList'] for x in self.collect.aggregate([
            {"$match": {param: value}},
            {"$project": {"itemId": 1, "date": 1, "_id": 0}},
            {"$group": {"_id": "$itemId"}},
            {"$limit": 20},
            {"$lookup": {
                "from": "comment",
                "localField": "_id",
                "foreignField": "itemId",
                "as": "commentList"
            }},
            {"$match": {"commentList": {"$ne": []}}},
            {"$match": {"commentList.updateTime": {"$gt": time}}},
            {"$project": {"commentList.commentContent": 1, "_id": 0}}
        ])]

    def shopCiYun(self):
        self.collect = self.SDcombine
        temp = self.getBrandData(self.paramList[0], self.paramList[1], 0)  # 不需要一周内时间范围
        data = [x['commentContent'] for y in temp for x in y if (x['commentContent'] != '')]
        if (len(data) < 200):
            itemId, sellerId = [x for x in self.collect.aggregate([
                {"$match": {"shopUrl": self.paramList[1]}},
                {"$project": {"itemId": 1, "sellerId": 1, "_id": 0, "monthSales": 1}},
                {"$sort": {"monthSales": -1}},
                {"$limit": 1},
                {"$project": {"itemId": 1, "sellerId": 1}}
            ])][0].values()
            self.itemComment(itemId, sellerId)
            data = self.newCommentList
        # ------3.38s-----
        b = [j for i in data for j in self.split_jieba(i)]
        di = dict(Counter(b))
        self.data = [list(x) for x in sorted(di.items(), key=lambda d: d[1], reverse=True)[:50]]

    def brandCiYun(self):
        '''根据品牌名称获取其一周评论词云数据'''
        self.collect = self.SDcombine
        temp = self.getBrandData(self.paramList[0], self.paramList[1], 1522339200)
        data = [x['commentContent'] for y in temp for x in y if (x['commentContent'] != '')]
        if (len(data) < 500):
            '''如果评论数小于500则，取消时间限制,取所有评论'''
            temp = self.getBrandData(self.paramList[0], self.paramList[1], 0)
            data = [x['commentContent'] for y in temp for x in y if (x['commentContent'] != '')]
        # print(len(data))
        # start = time.time()

        #         ------3.38s-----
        b = [j for i in data for j in self.split_jieba(i)]
        di = dict(Counter(b));
        del di[' ']
        self.data = [list(x) for x in sorted(di.items(), key=lambda d: d[1], reverse=True)[:50]]

    def tm(self, url):
        try:
            JSON = ur.urlopen(url).read().decode('gbk')
        except:
            return
        js = json.loads(re.sub('\s+', '', JSON)[5:-1])
        # print([x['rateContent'] for x in list(js.values())[0]['rateList']])
        temp = [x['rateContent'] for x in list(js.values())[0]['rateList']]
        if (temp == []):
            return
        else:
            self.newCommentList += temp

    def itemComment(self, itemId, sellerId):
        self.newCommentList = []
        self.pool = ThreadPool(5)
        urls = [
            "https://rate.tmall.com/list_detail_rate.htm?ItemId=" + itemId + "&sellerId=" + sellerId + "&currentPage=" + str(
                i) + "&callback=json" for i in range(1, 6)]

        self.pool.map(self.tm, urls)
        self.pool.join()
        self.pool.close()

    def itemWeekDisplay(self):
        '''商品一周展现：itemId,此商品一周的曝光度'''
        self.collect = self.SDcombine
        temp = [(x['pageIndex'], x['itemIndex']) for x in self.collect.aggregate(
            [{"$match": {"itemId": "541476622873"}},
             {"$project": {"itemId": 1, "pageIndex": 1, "date": 1, "itemIndex": 1, "_id": 0}},
             {"$group": {"_id": {"data": "$date", "pageIndex": "$pageIndex", "itemIndex": "$itemIndex"}}},
             {"$sort": {"_id.data": -1}},
             {"$project": {"pageIndex": "$_id.pageIndex", "itemIndex": "$_id.itemIndex", "_id": 0}},
             {"$limit": 7}
             ])]
        self.data = [int(1 / (x[0] * 60 + x[1]) * 10000) for x in temp]

    def itemEmotion(self):
        '''调用情感分析接口'''
        tempComment = [x['commentContent'] for x in self.comment.aggregate([
            {"$match": {"itemId": self.paramList[1], "updateTime": {"$gt": 1522339200}}},
            {"$project": {"commentContent": 1, "_id": 0}},
        ])]
        valueList = [self.sentiments_analysis(x) for x in tempComment]
        endIndex = int(len(tempComment) / 7) * 7  # 按7等份得出最后的索引
        avg = int(len(tempComment) / 7)  # 每等份多少个值
        daySum = 0
        weekList = []
        for i in range(endIndex + 1):
            if (i % avg == 0 and i != 0):
                weekList.append(daySum)
                daySum = 0
            else:
                daySum += valueList[i]
        self.data = weekList

    def sentiments_analysis(self, text):
        '''计算每个句子的情感分数'''
        s = jieba.cut(text)
        score = []
        if s == []:
            return None
        for i in s:
            score.append(SnowNLP(i).sentiments)
        if (len(score) == 0):
            return 0
        avg_score = sum(score) / len(score)
        return avg_score

    def shopTopItem(self):
        self.collect = self.SDcombine
        temp = [x for x in self.collect.aggregate(
            [{"$match": {"shopUrl": self.paramList[1]}},
             {"$project": {"itemId": 1, "title": 1, "_id": 0}},
             {"$group": {"_id": "$itemId", "title": {"$push": "$title"}, "sum": {"$sum": 1}}}, {"$sort": {"sum": -1}},
             {"$project": {"_id": 1, "sum": 1, "shopUrl": {"$slice": ["$title", -1, 1]}}}
             ])][:5]
        self.data = [['https://detail.tmall.com/item.htm?id=' + x['_id'], x['sum'], x['shopUrl'][0]] for x in temp]

    def shopEmotion(self):
        temp = [x for x in self.SDcombine.aggregate([
            {"$match": {"shopUrl": self.paramList[1]}},
            {"$project": {"itemId": 1, "_id": 0}},
            {"$group": {"_id": "$itemId"}},
            {"$lookup": {
                "from": "comment",
                "localField": "_id",
                "foreignField": "itemId",
                "as": "commentList"
            }},
            {"$match": {"commentList": {"$ne": []}}},
            {"$match": {"commentList.updateTime": {"$gt": 1522339200}}},
            {"$project": {"commentList.commentContent": 1, "_id": 1}}
        ])]
        npList = []
        for i in temp[:5]:  # 每一个id
            itemCommentList = [x['commentContent'] for x in i['commentList']]
            valueList = [self.sentiments_analysis(x) for x in itemCommentList]
            endIndex = int(len(itemCommentList) / 7) * 7  # 按7等份得出最后的索引
            if (endIndex == 0):
                continue
            avg = int(len(itemCommentList) / 7)  # 每等份多少个值
            daySum = 0
            weekList = []
            for j in range(endIndex + 1):
                if (j % avg == 0 and j != 0):
                    weekList.append(daySum)
                    daySum = 0
                else:
                    daySum += valueList[j]
            npList.append(weekList)
        self.data = list(np.sum(npList, axis=0))

    def min_max_range(self, x, range_values):
        return [
            round(((xx - min(x)) / (1.0 * (max(x) - min(x)))) * (range_values[1] - range_values[0]) + range_values[0],
                  2) for xx in x]


# url='http://localhost:9000/data/item/itemInfo?price_range=25%2C75&sales_range=25%2C1075&collect_range=25%2C10075&start_date=0&end_date=-1&limit=10&offset=10&search=&_=1524373470930'
# url1='http://localhost:9000/data/shop/shopInfo?stock_range=25%2C1000&sales_range=0%2C1000&collect_range=0%2C20000&start_date=0&end_date=-1&limit=25&offset=0&search=&_=1524989156915'
# url2='http://localhost:9000/data/brand/brandInfo?sales_range=0%2C1000&stock_range=0%2C1000&collect_range=0%2C1000&start_date=0&end_date=-1&limit=25&offset=0&search=&_=1524989156915'
# url3=''
bin = SearchServer()
# # print bin.start(url=url1)
# # print(bin.start(method='itemDetail', param='itemId=558661278181'))
# print(bin.start(method='itemSource', param='itemId=541476622873'))
# # print(bin.start(method='itemTrend', param='itemId=541476622873'))
# print(bin.start(method='shopCiYun', param='shopUrl=//kairuidihe.tmall.com'))
# # itemSimilarity
# # print(bin.start(method='brandTrend', param='brandName=\\xa0蓝色私语'))
# print(bin.start(method='brandSearchDisplay', param='brandName=\\xa0蓝色私语'))
# # print(bin.start(method='brandTopShop', param='brandName=\\xa0众晟'))
# # print(bin.start(method='brandTopItem', param='brandName=\\xa0众晟'))
# # brandCiYun
# # brandShopArea
# # print(bin.start(method='shopSource', param='shopUrl=//zhongshengcl.tmall.com'))
# # print(bin.start(method='shopTrend', param='shopUrl=//kairuidihe.tmall.com'))
# print(bin.start(method='shopSearchDisplay', param='shopUrl=//kairuidihe.tmall.com'))
bin = SearchServer()
print(bin.start(method='shopCiYun', param='shopUrl=//aipulism.tmall.com'))
# data = bin.start(method='brandCiYun', param='brandName=\\xa0众晟')
# print(data)
