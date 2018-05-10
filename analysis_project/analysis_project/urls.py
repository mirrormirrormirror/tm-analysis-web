"""analysis_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
import analysis_app.views as views

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns = [
    path('item_search/', views.item_search),
    path('dian_pu_analysis/', views.dian_pu_analysis),
    path('brand/', views.brand),
    path('dian_pu/', views.dian_pu),
    path('brand_search/', views.brand_search),
    url(r'item_analysis', views.item_analysis),
    url(r'^admin/', admin.site.urls),
    url(r'data/item/itemInfo', views.test_data),
    url(r'data/shop/shopInfo', views.shop_data),
    url(r'data/brand/brandInfo', views.brand_data),

    url(r'itemTrend', views.itemTrend),
    url(r'shopTrend', views.shopTrend),
    url(r'brandTrend', views.brandTrend),
    url(r'itemWeekDisplay', views.itemWeekDisplay),
    url(r'itemEmotion', views.itemEmotion),
    url(r'shopTopItem', views.shopTopItem),
    url(r'shopSearchDisplay', views.shopSearchDisplay),
    url(r'shopEmotion', views.shopEmotion),


    url(r'itemDetail', views.itemDetail),  #
    url(r'itemSource', views.itemSource),  #
    url(r'brandSearchDisplay', views.brandSearchDisplay),
    url(r'brandTopShop', views.brandTopShop),
    url(r'brandTopItem', views.brandTopItem),
    url(r'shopSource', views.shopSource),
    url(r'brandCiYun', views.brandCiYun),
    url(r'itemCiYun', views.itemCiYun),
    url(r'shopCiYun', views.shopCiYun),
    url(r'brandShopArea', views.brandShopArea),
    url(r'brandSource', views.brandSource),

    url(r'test', views.test),
    url(r'index', views.example),
    url(r'register', views.register),
    url(r'login', views.login),
]
