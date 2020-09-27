#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/23 17:03
# @Author  : hui
# @Email   : huihuil@bupt.edu.cn
# @File    : controller.py
import json

from django.http import HttpResponse
from django.db import connection
def list1(request):
    res = []
    cursor = connection.cursor()
    sql = "select number,province,city,area,info,time from disaster_info; "
    cursor.execute(sql)
    data = cursor.fetchall();
    for row in data:
        res.append({
            'number':row[0],
            'province':row[1],
            'city':row[2],
            'area':row[3],
            'info':row[4],
            'time':row[5].strftime('%Y-%m-%d %H:%M:%S')
        })
    res = json.dumps(res,ensure_ascii=False)
    return HttpResponse(res)