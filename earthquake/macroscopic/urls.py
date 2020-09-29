#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/23 17:04
# @Author  : hui
# @Email   : huihuil@bupt.edu.cn
# @File    : urls.py
from django.urls import path,include
from . import controller
app_name = 'earthquake_macroscopic'
urlpatterns = [
    # 地图展示
    path('map1',controller.map1),
    path('map2',controller.map2),
    # 折线图展示
    path('line1',controller.line1),
    # 直方图展示
    path('bar1',controller.bar1),
    # 饼图展示
    path('pie1',controller.pie1),
    # 列表展示
    path('list1',controller.list1),
]
