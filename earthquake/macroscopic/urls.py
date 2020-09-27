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
    path('list1',controller.list1),
]
