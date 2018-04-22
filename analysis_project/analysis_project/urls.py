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
from analysis_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns = [
    path('item_search/', views.item_search),
    path('dian_pu_analysis/', views.dian_pu_analysis),
    path('brand/', views.brand),
    path('dian_pu/', views.dian_pu),
    path('brand_search/', views.brand_search),
    url(r'item_analysis', views.item_analysis),  #
    url(r'^admin/', admin.site.urls),
    url(r'data', views.test_data),
    url(r'test', views.test),
    url(r'index', views.example),
    url(r'register', views.register),
    url(r'login', views.login),

    url(r'show_table', views.show_table)
]
