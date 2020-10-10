#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/23 17:03
# @Author  : hui
# @Email   : huihuil@bupt.edu.cn
# @File    : controller.py
import datetime
import json
from django.http import HttpResponse
from django.db import connection
from ..models import disaster_info
from django.utils import timezone

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
    def type_judge(time):
        # time = utc.localize(time)
        now_time = timezone.now()
        print(now_time)
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
        records = disaster_info.objects.filter(province=province, city=city).order_by('-time')
        nums = len(records)
        time = records.first().time
        info = records.first().info
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
    records = disaster_info.objects.order_by("-time")
    for record in records:
        res.append({
            'number': record.number,
            'province': record.province,
            'city': record.city,
            'area': record.area,
            'info': record.info,
            'time': record.time.strftime('%Y-%m-%d %H:%M:%S'),
            'authority': record.authority,  # 可信度，1高可信度，2为低可信度
        })
    res = {
        "code": 200,
        "msg": "success",
        "totalCount": len(records),
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

def list3(request):
    province = "河北省"
    city = "唐山市"
    res = []
    records = disaster_info.objects.filter(province=province, city=city).order_by("-time")
    for record in records:
        res.append({
            'number': record.number,
            'province': record.province,
            'city': record.city,
            'area': record.area,
            'info': record.info,
            'time': record.time.strftime('%Y-%m-%d %H:%M:%S'),
            'authority': record.authority,  # 可信度，1高可信度，2为低可信度
        })
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)


