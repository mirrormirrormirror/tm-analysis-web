# coding:utf-8
dictColumn = {'price_range': 'price', 'sales_range': 'monthSales', 'collect_range': 'collectNum'}


def Info(infoName, temp1):
    '''item shop brand的info汇总'''
    if (infoName == 'item_itemInfo'):
        columns = {"itemId": 1, "title": 1, "price": 1, "collectNum": 1, "totalQuantity": 1, "monthSales": 1, "_id": 0}
    elif (infoName == 'shop_shopInfo'):
        columns = {'shopName': 1, 'shopUrl': 1, 'monthSales': 1, 'totalQuantity': 1, 'collectNum': 1, '_id': 0}
    offset = 0
    limit = 0
    baseQuery = {'$and': []}
    for i in temp1:
        if ('range' in i[0]):
            split = [float(x) for x in i[1].split('%2C')]
            baseQuery['$and'].append({dictColumn[i[0]]: {'$gt': split[0]}})
            baseQuery['$and'].append({dictColumn[i[0]]: {'$lt': split[1]}})
            continue
        if (i[0] == 'start_date'):
            if (i[1] == '0'):
                continue
            else:
                tempDate = i[1][:1] + '.' + i[1][1:]
                baseQuery['$and'].append({'updatetime': {'$gt': tempDate}})
        if (i[0] == 'end_date'):
            if (i[1] == '-1'):
                continue
            else:
                tempDate = i[1][:1] + '.' + i[1][1:]
                baseQuery['$and'].append({'updatetime': {'$lt': tempDate}})
        if (i[0] == 'limit'):
            limit = i[1]
            continue
        if (i[0] == 'offset'):
            offset = i[1]
            continue
    return baseQuery, int(limit), int(int(offset) / int(limit)), columns


def brand_brandInfo(temp1):
    ''''''

    return


def item_itemDetail(temp1):
    pass


def item_itemSource(temp1):
    pass


def item_itemTrend(temp1):
    pass


def item_itemCiYun(temp1):
    pass


def item_itemSimilarity(temp1):
    pass


def brand_brandTrend(temp1):
    pass


def brand_brandSource(temp1):
    pass


def brand_brandSearchDisplay(temp1):
    pass


def brand_brandTopShop(temp1):
    pass


def brand_brandTopItem(temp1):
    pass


def brand_brandCiYun(temp1):
    pass


def brand_brandShopArea(temp1):
    pass


def shop_shopSource(temp1):
    pass


def shop_shopTrend(temp1):
    pass


def shop_shopSearchDisplay(temp1):
    pass
