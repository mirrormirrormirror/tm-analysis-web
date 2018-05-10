import  jieba
self.stopword = open('stopword.txt', 'r').read().split('\n')


def split_jieba(self, seq):
    return [x for x in jieba.cut(seq) if x not in self.stopword]

def brandCiYun(self):
    '''根据品牌名称获取其一周评论词云数据'''
    self.collect = self.SDcombine
    temp = [x['commentList'] for x in self.collect.aggregate([
        {"$match": {"brand": self.paramList[1]}},
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
        {"$match": {"commentList.updateTime": {"$gt": 1522339200}}},
        {"$project": {"commentList.commentContent": 1, "_id": 0}}
    ])]
    data = [x['commentContent'] for y in temp for x in y if (x['commentContent'] != '')]
    # start = time.time()

    #         ------3.38s-----
    b = [j for i in data for j in self.split_jieba(i)]
    di = dict(Counter(b))
    self.data = sorted(di.items(), key=lambda d: d[1], reverse=True)[:50]