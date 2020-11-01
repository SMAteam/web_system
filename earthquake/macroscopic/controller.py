#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/23 17:03
# @Author  : hui
# @Email   : huihuil@bupt.edu.cn
# @File    : controller.py
import datetime
import json
import re

from django.http import HttpResponse
from django.db import connection
from ..models import DisasterInfo
from django.utils import timezone
import redis
pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
earthquake_id = '1_1'
#
# 地图展示
#
# 展示每个省份的地震数量
def map1(request):
    res = []
    cursor = connection.cursor()
    sql = "select province,count(*) from disaster_info where authority='1' group by province;"
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
# 展示每个省地震的微博讨论数量
def map2(request):
    r = redis.Redis(connection_pool = pool)
    if r.exists("earthquake_macroscopic_map2"):
        res = r.get("earthquake_macroscopic_map2")
        return HttpResponse(res)
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
# 地图标记每个省市的最新地震情况
def map3(request):
    def type_judge(time):
        # time = utc.localize(time)
        now_time = timezone.now()
        if now_time - datetime.timedelta(days=2) < time:
            return 1
        elif now_time - datetime.timedelta(days=60) < time:
            return 2
        else:
            return 3
    res = []
    cursor = connection.cursor()
    sql = f"select lng, lat, province, city from loc as a, disaster_info as b where a.sheng=b.province and a.shi=b.city group by lat, lng, province, city;"
    cursor.execute(sql)
    data = cursor.fetchall()
    for row in data:
        lng = row[0]
        lat = row[1]
        province = row[2]
        city = row[3]
        records = DisasterInfo.objects.filter(province=province, city=city).order_by('-time')
        nums = len(records)
        time = None
        info = None
        authority = None
        for record in records:
            time = record.time
            info = record.info
            if record.authority == '1' or type_judge(time) == 1:
                authority = '1'
                break
        if authority == None:
            continue
        res.append({
            "lng": lng,# 经度
            "lat": lat,# 维度
            "province": province,# 省
            "city": city, # 市
            "title": "地震信息",
            "content1": time.strftime('%Y-%m-%d %H:%M:%S') + province + city + "发生" + info,
            "content2": "近年来共发生" + str(nums)+ "次地震",
            "type": type_judge(time) # 1代表2天内发生过地震，2代表2个月内发生过地震，3代表其他
        })
    res = {
        "code": 200,
        "msg": "success",
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# def map3(request):
#     province = request.GET.get('province','')
#     task_id = request.GET.get('task_id', '')
#     res = []
#     cursor = connection.cursor()
#     sql = f"select province, city, area, time, info from disaster_info where province='{province}' and task_id='{task_id}';"
#     cursor.execute(sql)
#     data = cursor.fetchall()
#     for row in data:
#         res.append({
#             "province": row[0],
#             "city": row[1],
#             "area": row[2],
#             "time": row[3],
#             "info": row[4],
#         })
#     res = {
#         "code": 200,
#         "msg": "success",
#         "data": res
#     }
#     res = json.dumps(res, ensure_ascii=False)
#     return HttpResponse(res)
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
# 地震微博各月数量
def bar1(request):
    r = redis.Redis(connection_pool = pool)
    if r.exists("earthquake_macroscopic_bar1"):
        res = r.get("earthquake_macroscopic_bar1")
        return HttpResponse(res)
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
# 展示不同等级的地震数量分布情况
def pie1(request):
    res = []
    count = {
        "弱震":0,
        "有感地震": 0,
        "中强震": 0,
        "强震": 0,
    }
    cursor = connection.cursor()
    records = DisasterInfo.objects.filter(task_id=earthquake_id, authority='1')
    for record in records:
        if  float(record.grade) < 3.0:
            count["弱震"] += 1
        elif float(record.grade) >= 3.0 and float(record.grade) <= 4.5:
            count["有感地震"] += 1
        elif float(record.grade) > 4.5 and float(record.grade) < 6.0:
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
# 展示全国地震的信息
def list1(request):
    res = []
    records = DisasterInfo.objects.order_by("-time")
    for record in records:
        authority = '1'
        if record.grade == '-100' or record.authority == '0':
            authority = '0'
        res.append({
            'number': record.number,
            'province': record.province,
            'city': record.city if record.city != "-100" else "",
            'area': record.area if record.area != "-100" else "",
            'info': record.info if record.info != "-100" else "",
            'time': record.time.strftime('%Y-%m-%d %H:%M:%S'),
            'authority': authority,  # 可信度，1高可信度，0为低可信度
        })
    res = {
        "code": 200,
        "msg": "success",
        "totalCount": len(records),
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 帖子列表展示
def list2(request):
    r = redis.Redis(connection_pool = pool)
    if r.exists("earthquake_macroscopic_list2"):
        res = r.get("earthquake_macroscopic_list2")
        return HttpResponse(res)
    res =[]
    cursor = connection.cursor()
    sql = 'select post_content,comment_num,like_num,forward_num,post_time,user_id,post_id from (select post_content,comment_num,like_num,forward_num,post_time,user_id,a.post_id from weibo_post as a, post_extra as b where a.task_id=b.task_id and a.post_id = b.post_id order by post_time desc limit 1000) as temp order by post_time desc, forward_num desc,comment_num desc;'
    cursor.execute(sql)
    data = cursor.fetchall()
    for row in data:
        res.append({
            'user_id': row[5],
            'post_time': row[4].strftime('%Y-%m-%d %H:%M:%S'),
            'forward_num': row[3],
            'comment_num': row[1],
            'like_num': row[2],
            'post_content': re.sub("<#>|</#>|<@>.*?</@>|<u>.*?</u>", '', row[0]),
            'post_url': "https://weibo.com/" + str(row[5]) + "/" + str(row[6]) + "/"
        })
    res = {
        "code": 200,
        "msg": "success",
        "totalCount": 1000,
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 展示具体某个省市的近期地震信息
def list3(request):
    province = request.GET.get("province", "河北省")
    city = request.GET.get("city", "唐山市")
    res = []
    records = DisasterInfo.objects.filter(province=province, city=city).order_by("-time")
    for record in records:
        authority = '1'
        if record.grade == '-100' or record.authority == '0':
            authority = '0'
        res.append({
            'number': record.number,
            'province': record.province,
            'city': record.city,
            'area': record.area,
            'info': record.info,
            'time': record.time.strftime('%Y-%m-%d %H:%M:%S'),
            'authority': authority,  # 可信度，1高可信度，0为低可信度
        })
    res = {
        "code": 200,
        "msg": "success",
        "totalCount": 1000,
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)


