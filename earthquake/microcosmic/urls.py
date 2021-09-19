#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/23 17:04
# @Author  : hui
# @Email   : huihuil@bupt.edu.cn
# @File    : urls.py
#!/usr/bin/env python
from django.conf.urls import url
from django.urls import path,include
from . import controller


app_name = 'earthquake_microcosmic'
urlpatterns = [
    # 地图展示
    path('list1',controller.list1),
    path('list2',controller.list2),

    path('wordcloud1',controller.wordcloud1),
    path('topiccloud1',controller.topiccloud1),
    #
    path('basestatistics1',controller.basestatistics1),
    # 折线图展示
    path('heattrend1',controller.heattrend1),
    # 发帖地分布
    path('postlocmap1',controller.postlocmap1),
    # 事件线
    path('eventline1',controller.eventline1),
    # 知识图谱
    path('entitymatch', controller.entitymatch)

]
