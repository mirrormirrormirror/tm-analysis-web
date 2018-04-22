from django.shortcuts import render
from analysis_app.migrations.service.user_service import userLogin
from django.shortcuts import render

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
    return render(request, '品牌详细分析.html')


def dian_pu_analysis(request):
    return render(request, '店铺详细分析.html')


def dian_pu(request):
    return render(request, '店铺搜索.html')


def brand_search(request):
    return render(request, '品牌搜索.html')


def item_analysis(request):
    return render(request, "商品详情分析.html")
    # return render(request, "table.html")
    # return render(request,"某行业二级类目销量分布图.html")
    # return render(request, '某行业卖家分布图.html')
    # return render(request, '热门行业商品销量对比走势图.html')


def test_data(request):
    return render(request, "test_item_data.json")


def test(requests):
    return render(requests, "test.html")


def show_table(request):
    if request.method == "GET":
        print(request.GET)
        limit = request.GET.get('limit')  # how many items per page
        offset = request.GET.get('offset')  # how many items in total in the DB
        search = request.GET.get('search')
        sort_column = request.GET.get('sort')  # which column need to sort
        order = request.GET.get('order')  # ascending or descending
        if search:  # 判断是否有搜索字
            all_records = models.Asset.objects.filter(id=search, asset_type=search, business_unit=search, idc=search)
        else:
            all_records = models.Asset.objects.all()  # must be wirte the line code here

        if sort_column:  # 判断是否有排序需求
            sort_column = sort_column.replace('asset_', '')
            if sort_column in ['id', 'asset_type', 'sn', 'name', 'management_ip', 'manufactory',
                               'type']:  # 如果排序的列表在这些内容里面
                if order == 'desc':  # 如果排序是反向
                    sort_column = '-%s' % (sort_column)
                all_records = models.Asset.objects.all().order_by(sort_column)
            elif sort_column in ['salt_minion_id', 'os_release', ]:
                # server__ 表示asset下的外键关联的表server下面的os_release或者其他的字段进行排序
                sort_column = "server__%s" % (sort_column)
                if order == 'desc':
                    sort_column = '-%s' % (sort_column)
                all_records = models.Asset.objects.all().order_by(sort_column)
            elif sort_column in ['cpu_model', 'cpu_count', 'cpu_core_count']:
                sort_column = "cpu__%s" % (sort_column)
                if order == 'desc':
                    sort_column = '-%s' % (sort_column)
                all_records = models.Asset.objects.all().order_by(sort_column)
            elif sort_column in ['rams_size', ]:
                if order == 'desc':
                    sort_column = '-rams_size'
                else:
                    sort_column = 'rams_size'
                all_records = models.Asset.objects.all().annotate(rams_size=Sum('ram__capacity')).order_by(sort_column)
            elif sort_column in [
                'localdisks_size', ]:  # using variable of localdisks_size because there have a annotation below of this line
                if order == "desc":
                    sort_column = '-localdisks_size'
                else:
                    sort_column = 'localdisks_size'
                # annotate 是注释的功能,localdisks_size前端传过来的是这个值，后端也必须这样写，Sum方法是django里面的，不是小写的sum方法，
                # 两者的区别需要注意，Sum（'disk__capacity‘）表示对disk表下面的capacity进行加法计算，返回一个总值.
                all_records = models.Asset.objects.all().annotate(localdisks_size=Sum('disk__capacity')).order_by(
                    sort_column)

            elif sort_column in ['idc', ]:
                sort_column = "idc__%s" % (sort_column)
                if order == 'desc':
                    sort_column = '-%s' % (sort_column)
                all_records = models.Asset.objects.all().order_by(sort_column)

            elif sort_column in ['trade_date', 'create_date']:
                if order == 'desc':
                    sort_column = '-%s' % sort_column
                all_records = models.Asset.objects.all().order_by(sort_column)

        all_records_count = all_records.count()

        if not offset:
            offset = 0
        if not limit:
            limit = 20  # 默认是每页20行的内容，与前端默认行数一致
        pageinator = Paginator(all_records, limit)  # 开始做分页

        page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_records_count, 'rows': []}  # 必须带有rows和total这2个key，total表示总页数，rows表示每行的内容

        for asset in pageinator.page(page):
            ram_disk = get_ram_sum_size(asset.id)  # 获取磁盘和内存的大小
            # 下面这些asset_开头的key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            response_data['rows'].append({
                "asset_id": '<a href="/asset/asset_list/%d" target="_blank">%d</a>' % (asset.id, asset.id),
                "asset_sn": asset.sn if asset.sn else "",
                "asset_business_unit": asset.business_unit if asset.business_unit else "",
                "asset_name": asset.name if asset.name else "",
                "asset_management_ip": asset.management_ip if asset.management_ip else "",
                "asset_manufactory": asset.manufactory.manufactory if hasattr(asset, 'manufactory') else "",
                "asset_type": asset.asset_type if asset.asset_type else "",
                "asset_os_release": asset.server.os_release if hasattr(asset, 'server') else "",
                "asset_salt_minion_id": asset.server.salt_minion_id if hasattr(asset, 'server') else "",
                "asset_cpu_count": asset.cpu.cpu_count if hasattr(asset, 'cpu') else "",
                "asset_cpu_core_count": asset.cpu.cpu_core_count,
                "asset_cpu_model": asset.cpu.cpu_model if hasattr(asset, 'cpu') else "",
                "asset_rams_size": ram_disk[0] if ram_disk[0] else "",
                "asset_localdisks_size": ram_disk[1] if ram_disk[1] else "",
                "asset_admin": asset.admin.username if asset.admin else "",
                "asset_idc": asset.idc if asset.idc else "",
                "asset_trade_date": asset.trade_date.strftime('%Y-%m-%d %H:%M') if asset.trade_date else "",
                "asset_create_date": asset.create_date.strftime("%Y-%m-%d %H:%M") if asset.create_date else "",
                "update_date": asset.update_date.strftime("%Y-%m-%d %H:%M") if asset.update_date else "",
            })

        return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式
