from django.http import HttpResponse
from django.shortcuts import render
from analysis_app.migrations.service.user_service import userLogin
from django.shortcuts import render
from analysis_app.searchInfo import SearchServer
import json
from analysis_app.migrations.service.user_service import userLogin


# Create your views here.
def item_search(request):
    return render(request, 'item_search.html')


def example(request):
    return render(request, 'example.html')


def register(request):
    return render(request, 'register.html')


def login(request):
    return render(request, 'login.html')


def brand(request):
    brand = request.GET['brand']
    bin = SearchServer()
    brandTopShop = bin.start(method='brandTopShop', param='brand=' + brand[1:])  # brandTopItem
    brandTopItem = bin.start(method='brandTopItem', param='brand=' + brand[1:])
    brandName = brand.replace("\\", "").replace("xa0", "")
    return render(request, '品牌详细分析.html',
                  {'brandTopShop': brandTopShop, 'brandTopItem': brandTopItem, 'brand': brand, "brandName": brandName})


def dian_pu_analysis(request):
    shopUrl = request.GET['shopUrl']
    bin = SearchServer()
    shopImage = bin.shopImage(shopUrl)
    shopTopItem = bin.start(method='shopTopItem', param='shopUrl=' + shopUrl)
    return render(request, '店铺详细分析.html', {'shopImage': shopImage, 'shopTopItem': shopTopItem, 'shopUrl': shopUrl})


def dian_pu(request):
    return render(request, '店铺搜索.html')


def brand_search(request):
    return render(request, '品牌搜索.html')


def item_analysis(request):
    itemId = request.GET['itemId']
    bin = SearchServer()
    data = bin.start(method='itemDetail', param='itemId=' + itemId)
    s = data[0]["destailsDict"]
    s = s.replace("[", "").replace("]", "").replace("}", "").replace("{", "").replace("'", "").replace("'", "").replace(
        "\\xa0", "")
    details = s.split("，")
    titleAndItemImg = bin.itemImage(itemId)
    title = titleAndItemImg[0]
    itemImg = titleAndItemImg[1]
    print(details)
    return render(request, "商品详情分析.html", {'details': details, 'itemImg': itemImg, 'title': title, 'itemId': itemId})


def test_data(request):
    url = request.get_full_path()
    # url = 'http://localhost:9000/data/?price_range=0%2C1000&sales_range=0%2C1000&collect_range=0%2C1000&start_date=0&end_date=-1&limit=25&offset=0&search=&_=1524989156915 '
    server = SearchServer()
    data = server.start(url)
    # data["total"] = 100
    return HttpResponse(json.dumps(data), content_type="application/json")


def shop_data(request):
    url = request.get_full_path()
    # url = 'http://localhost:9000/data/?price_range=0%2C1000&sales_range=0%2C1000&collect_range=0%2C1000&start_date=0&end_date=-1&limit=25&offset=0&search=&_=1524989156915 '
    server = SearchServer()
    data = server.start(url)
    # data["total"] = 100
    return HttpResponse(json.dumps(data), content_type="application/json")


def brand_data(request):
    url = request.get_full_path()
    # url = 'http://localhost:9000/data/?price_range=0%2C1000&sales_range=0%2C1000&collect_range=0%2C1000&start_date=0&end_date=-1&limit=25&offset=0&search=&_=1524989156915 '
    server = SearchServer()
    data = server.start(url)
    # data["total"] = 100
    return HttpResponse(json.dumps(data), content_type="application/json")


def itemTrend(request):
    itemId = request.GET['itemId']
    bin = SearchServer()
    data = bin.start(method='itemTrend', param='itemId=' + itemId)
    return HttpResponse(json.dumps(data), content_type="application/json")


def shopTrend(request):
    shopUrl = request.GET['shopUrl']
    bin = SearchServer()
    data = bin.start(method='shopTrend', param='shopUrl=' + shopUrl)
    return HttpResponse(json.dumps(data), content_type="application/json")


def brandTrend(request):
    brand = request.GET['brand']
    bin = SearchServer()
    data = bin.start(method='brandTrend', param='brandName=' + brand)
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")


def itemDetail(request):
    itemId = request.GET['itemId']
    bin = SearchServer()
    data = bin.start(method='itemDetail', param='itemId=' + itemId)
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")


def itemSource(request):
    itemId = request.GET['itemId']
    bin = SearchServer()
    data = bin.start(method='itemSource', param='itemId=' + itemId)
    return HttpResponse(json.dumps(data), content_type="application/json")


def brandSearchDisplay(request):
    brand = request.GET['brand']
    bin = SearchServer()
    data = bin.start(method='brandSearchDisplay', param='brandName=' + brand)
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")


def brandTopShop(request):
    brand = request.GET['brand']
    bin = SearchServer()
    data = bin.start(method='brandTopShop', param='brandName=' + brand)
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")


def brandTopItem(request):
    brand = request.GET['brand']
    bin = SearchServer()
    data = bin.start(method='brandTopItem', param='brandName=' + brand)
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")


def shopSource(request):
    shopUrl = request.GET['shopUrl']
    bin = SearchServer()
    data = bin.start(method='shopSource', param='shopUrl=' + shopUrl)
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")


def brandCiYun(request):
    brand = request.GET['brand']
    bin = SearchServer()
    data = bin.start(method='brandCiYun', param='brand=' + brand)
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")


def shopCiYun(request):
    shopUrl = request.GET['shopUrl']
    bin = SearchServer()
    data = bin.start(method='shopCiYun', param='shopUrl=' + shopUrl)
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")


def itemCiYun(request):
    itemId = request.GET['itemId']
    bin = SearchServer()
    data = bin.start(method='itemCiYun', param='itemId=' + itemId)
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")


def brandShopArea(request):
    brand = request.GET['brand']
    bin = SearchServer()
    data = bin.start(method='brandShopArea', param='brand=' + brand)
    return HttpResponse(json.dumps(data), content_type="application/json")


def brandSource(request):
    brand = request.GET['brand']
    bin = SearchServer()
    data = bin.start(method='brandSource', param='brand=' + brand)
    return HttpResponse(json.dumps(data), content_type="application/json")


def itemWeekDisplay(request):
    itemId = request.GET['itemId']
    bin = SearchServer()
    data = bin.start(method='itemWeekDisplay', param='itemId=' + itemId)
    return HttpResponse(json.dumps(data), content_type="application/json")


def itemEmotion(request):
    itemId = request.GET['itemId']
    bin = SearchServer()
    data = bin.start(method='itemEmotion', param='itemId=' + itemId)
    return HttpResponse(json.dumps(data), content_type="application/json")


def shopTopItem(request):
    shopUrl = request.GET['shopUrl']
    bin = SearchServer()
    data = bin.start(method='shopTopItem', param='shopUrl=' + shopUrl)
    return HttpResponse(json.dumps(data), content_type="application/json")


def shopSearchDisplay(request):
    shopUrl = request.GET['shopUrl']
    bin = SearchServer()
    data = bin.start(method='shopSearchDisplay', param='shopUrl=' + shopUrl)
    return HttpResponse(json.dumps(data), content_type="application/json")


def shopEmotion(request):
    shopUrl = request.GET['shopUrl']
    bin = SearchServer()
    data = bin.start(method='shopEmotion', param='shopUrl=' + shopUrl)
    return HttpResponse(json.dumps(data), content_type="application/json")


def test(requests):
    return render(requests, "test.html")
