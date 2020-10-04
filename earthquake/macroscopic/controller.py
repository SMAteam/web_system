#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/23 17:03
# @Author  : hui
# @Email   : huihuil@bupt.edu.cn
# @File    : controller.py
import json
from django.http import HttpResponse
from django.db import connection
#
# 地图展示
#
def map1(request):
    res = []
    cursor = connection.cursor()
    sql = "select province,count(*) from disaster_info group by province;"
    cursor.execute(sql)
    data = cursor.fetchall()
    yingshe = {}
    for row in data:
        pro = row[0];
        yingshe[pro] = pro[:2];
    yingshe["内蒙古自治区"] = "内蒙古"
    yingshe["黑龙江省"] = "黑龙江"
    for row in data:
        res.append({
            "name": yingshe[row[0]],
            "value": row[1]
        })
    res = {
        "code": 200,
        "msg": "success",
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
def map2(request):
    res = []
    cursor = connection.cursor()
    sql = "select province,count(*) from disaster_info,post_extra where post_extra.cluster=disaster_info.number  group by province;"
    cursor.execute(sql)
    data = cursor.fetchall()
    yingshe = {}
    for row in data:
        pro = row[0];
        yingshe[pro] = pro[:2];
    yingshe["内蒙古自治区"] = "内蒙古"
    yingshe["黑龙江省"] = "黑龙江"
    for row in data:
        res.append({
            "name": yingshe[row[0]],
            "value": row[1]
        })
    res = {
        "code": 200,
        "msg": "success",
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
def map3(request):
    province = request.GET.get('province','')
    task_id = request.GET.get('task_id', '')
    res = []
    cursor = connection.cursor()
    sql = f"select province, city, area, time, info from disaster_info where province='{province}' and task_id='{task_id}';"
    cursor.execute(sql)
    data = cursor.fetchall()
    for row in data:
        res.append({
            "province": row[0],
            "city": row[1],
            "area": row[2],
            "time": row[3],
            "info": row[4],
        })
    res = {
        "code": 200,
        "msg": "success",
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
#
# 折线图展示
#
def line1(request):
    res = []
    cursor = connection.cursor()
    sql = "select DATE_FORMAT(time,'%Y-%m'),count(*) from disaster_info group by DATE_FORMAT(time,'%Y-%m');"
    cursor.execute(sql)
    data = cursor.fetchall();
    for row in data:
        res.append({
            "name": row[0],
            "value": row[1]
        })
    res = {
        "code": 200,
        "msg": "success",
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
#
# 直方图展示
#
def bar1(request):
    res = []
    cursor = connection.cursor()
    sql = "select DATE_FORMAT(post_time,'%Y-%m'),count(*) from post_extra as a,weibo_post as b where a.task_id=b.task_id and a.post_id=b.post_id group by DATE_FORMAT(post_time,'%Y-%m');"
    cursor.execute(sql)
    data = cursor.fetchall();
    for row in data:
        res.append({
            "name": row[0],
            "value": row[1]
        })
    res = {
        "code": 200,
        "msg": "success",
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
#
# 饼图展示
#
def pie1(request):
    res = []
    count = {
        "弱震":0,
        "有感地震": 0,
        "中强震": 0,
        "强震": 0,
    }
    cursor = connection.cursor()
    sql = "select grade from disaster_info;"
    cursor.execute(sql)
    data = cursor.fetchall()
    for row in data:
        if  row[0] == None or len(row[0]) == 0 or float(row[0]) < 3.0:
            count["弱震"] += 1
        elif float(row[0]) >= 3.0 and float(row[0]) <= 4.5:
            count["有感地震"] += 1
        elif float(row[0]) > 4.5 and float(row[0]) < 6.0:
            count["中强震"] += 1
        else:
            count["强震"] += 1
    for k,v in count.items():
        res.append({
            "name": k,
            "value": v
        })
    res = {
        "code": 200,
        "msg": "success",
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
#
# 列表展示
#
def list1(request):
    res = []
    cursor = connection.cursor()
    sql = "select number,province,city,area,info,time from disaster_info order by time desc;"
    cursor.execute(sql)
    data = cursor.fetchall();
    for row in data:
        res.append({
            'number': row[0],
            'province': row[1],
            'city': row[2],
            'area': row[3],
            'info': row[4],
            'time': row[5].strftime('%Y-%m-%d %H:%M:%S')
        })
    sql = "select count(*) from disaster_info;"
    cursor.execute(sql)
    data = cursor.fetchone();
    res = {
        "code": 200,
        "msg": "success",
        "totalCount": data[0],
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)

#  帖子列表展示
def list2(request):
    ret =[]
    cursor = connection.cursor()
    sql = 'select * from (select * from weibo_post limit 1000) as temp order by forward_num desc,comment_num desc;'
    cursor.execute(sql)
    data = cursor.fetchall();
    for row in data:
        ret.append({
            'user_id': row[1],
            'post_time': row[4].strftime('%Y-%m-%d %H:%M:%S'),
            'forward_num': row[5],
            'comment_num': row[6],
            'like_num': row[7],
            'post_content': row[3]
        })
    ret = {
        "code": 200,
        "msg": "success",
        "totalCount": 1000,
        "data": ret
    }
    ret = json.dumps(ret, ensure_ascii=False)
    return HttpResponse(ret)