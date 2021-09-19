#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/23 17:03
# @Author  : hui
# @Email   : huihuil@bupt.edu.cn
# @File    : controller.py
import datetime
import json
import re

import pymongo
from django.http import HttpResponse
from django.db import connection
from ..models import DisasterInfo
from django.utils import timezone
import redis
pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
client = pymongo.MongoClient(host = "152.136.59.62", port = 27017, maxPoolSize=50)

# 展示每个省份的地震数量
task = "1"
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
# 展示每个省地震的微博讨论数量
# 加了Redis缓存
def map2(request):
    redisConn = redis.Redis(connection_pool=pool)
    if redisConn.exists("earthquake_macroscopic_map2"):
        res = {
            "code": 200,
            "msg": "success",
            "data": eval(redisConn.get("earthquake_macroscopic_map2"))
        }
        res = json.dumps(res, ensure_ascii=False)
        return HttpResponse(res)
    db = client.admin
    db.authenticate('root', 'buptweb007')
    db = client.SocialMedia
    pipeline = [
        {"$match": {"task": task, "media": "1"}},
        {"$group": {"_id": "$province","count": {"$sum": 1}}}
    ]
    records = db.Posts.aggregate(pipeline, allowDiskUse=True)
    res = []
    for row in records:
        if  row.get("_id") != "海外" and row.get("_id") != "-100":
            res.append({
                "name": row.get("_id"),
                "value": int(row.get("count"))
            })
    redisConn.set("earthquake_macroscopic_map2",res)
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
# 每个月的地震数量
def line1(request):
    res = []
    cursor = connection.cursor()
    sql = f"select DATE_FORMAT(time,'%Y-%m'),count(*) from disaster_info where task='{task}' group by DATE_FORMAT(time,'%Y-%m');"
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
# 每个月相关微博数量
# 查询稍慢
def bar1(request):
    redisConn = redis.Redis(connection_pool=pool)
    if redisConn.exists("earthquake_macroscopic_bar1"):
        # res = json.loads(redisConn.get("earthquake_macroscopic_bar1"))
        res = {
            "code": 200,
            "msg": "success",
            "data": eval(redisConn.get("earthquake_macroscopic_bar1"))
        }
        res = json.dumps(res, ensure_ascii=False)
        return HttpResponse(res)
    db = client.admin
    db.authenticate('root', 'buptweb007')
    db = client.SocialMedia
    records = db.Posts.aggregate([{
        "$match": {
            "task": task
        }
    },{
        "$project": {
            "post_time": {
                "$dateToString": {
                    "format": "%Y-%m",
                    "date": "$post_time"
                }
            },
        }
    },{
        "$group": {
            "_id": "$post_time",
            "count": {
                "$sum": 1
            }
        }
    },{
        "$project": {
            "name": {
                "$dateFromString": {
                    "dateString": "$_id",
                }
            },
            "value": {
                "$abs": "$count"
            },
        }
    },{
        "$sort":{
            "name":1
        }
    }

    ])
    res = []
    for row in records:
        del row["_id"]
        row["name"] = row["name"].strftime('%Y-%m')
        res.append(row)
    redisConn.set("earthquake_macroscopic_bar1", res)
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
# 不同等级地震的数量分布情况
def pie1(request):
    res = []
    count = {
        "弱震":0,
        "有感地震": 0,
        "中强震": 0,
        "强震": 0,
    }
    records = DisasterInfo.objects.filter(task=task)
    for record in records:
        if  float(record.grade) < 3.0 and float(record.grade) != -100:
            count["弱震"] += 1
        elif float(record.grade) >= 3.0 and float(record.grade) <= 4.5:
            count["有感地震"] += 1
        elif float(record.grade) > 4.5 and float(record.grade) < 6.0:
            count["中强震"] += 1
        elif float(record.grade) >= 6.0:
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

# 展示全国地震的信息
def list1(request):
    res = []
    records = DisasterInfo.objects.filter(task=task).order_by("-time")
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
# 最新帖子消息展示
# 前台修改
def list2(request):
    media = request.GET.get("media", "1")
    db = client.admin
    db.authenticate('root', 'buptweb007')
    db = client.SocialMedia
    records = db.posts.find({
        "task": task,
        "media": str(media),
    }, {
        "_id": 0,
        "title": 1,
        "post_content": 1,
        "post_time": 1,
        "post_url": 1,
        "like_num": 1,
        "user_name": 1,
        "forward_num": 1,
        "comment_num": 1,
        "brief": 1,
        "media": 1,
        "label": 1
    }).sort([("post_time",-1)]).limit(1000)
    res = []
    for row in records:
        row["post_time"] = row["post_time"].strftime('%Y-%m-%d %H:%M:%S')
        if str(media) == "2":
            row['post_content'] = row['brief']
        else:
            row['post_content'] = re.sub("(<@>.*?</@>)|#|<#>|</#>|(<u>.*?</u>)", "", row['post_content'])
        res.append(row)
    res = {
        "code": 200,
        "msg": "success",
        "totalCount": len(res),
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 展示具体某个省市的近期地震信息，可以接受province,city,number
def list3(request):
    province = request.GET.get("province", "")
    city = request.GET.get("city", "")
    if province == "":
        row = DisasterInfo.objects.order_by("time").last()
        province = row.province
        city = row.city
    res = []
    if city != "":
        records = DisasterInfo.objects.filter(task=task,province=province, city=city).order_by("-time")
    else:
        records = DisasterInfo.objects.filter(task=task, province=province).order_by("-time")
    for record in records:
        authority = '1'
        if record.grade == '-100' or record.authority == '0':
            authority = '0'
        res.append({
            'number': record.number,
            'province': record.province,
            'city': record.city if record.city != "-100" else "",
            'area': record.area if record.area != "-100" else "",
            'info': record.info,
            'time': record.time.strftime('%Y-%m-%d %H:%M:%S'),
            'authority': authority,  # 可信度，1高可信度，0为低可信度
        })
    res = {
        "code": 200,
        "msg": "success",
        "province": province,
        "city": city,
        "totalCount": len(res),
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 地震事件总数量，舆情总数量统计
def basestatistics(request):
    redisConn = redis.Redis(connection_pool=pool)
    # redisConn.delete("earthquake_macroscopic_basestatistics")
    if redisConn.exists("earthquake_macroscopic_basestatistics"):
        res = {
            "code": 200,
            "msg": "success",
            "data": eval(redisConn.get("earthquake_macroscopic_basestatistics"))
        }
        res = json.dumps(res, ensure_ascii=False)
        return HttpResponse(res)
    db = client.admin
    db.authenticate('root', 'buptweb007')
    db = client.SocialMedia
    countTotal = db.posts.find({
        "task": task,
        "label": "1"
    }).count()
    countEvent = DisasterInfo.objects.filter(task=task).count()
    data = {}
    data['countTotal'] = countTotal
    data['countEvent'] = countEvent
    res = {
        "code": 200,
        "msg": "success",
        "data": data
    }
    # redisConn.set("earthquake_macroscopic_basestatistics", data)
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
def redisCache(request):
    task = "1"
    client = pymongo.MongoClient(host="152.136.59.62", port=27017, maxPoolSize=50)
    redisConn = redis.Redis(connection_pool=pool)

    db = client.admin
    db.authenticate('root', 'buptweb007')
    db = client.SocialMedia
    pipeline = [
        {"$match": {"task": task, "media": "1"}},
        {"$group": {"_id": "$province", "count": {"$sum": 1}}}
    ]
    records = db.Posts.aggregate(pipeline)
    res = []
    for row in records:
        if row.get("_id") != "海外" and row.get("_id") != "-100":
            res.append({
                "name": row.get("_id"),
                "value": int(row.get("count"))
            })
    redisConn.set("earthquake_macroscopic_map2", res)

    records = db.Posts.aggregate([{
        "$match": {
            "task": task
        }
    }, {
        "$project": {
            "post_time": {
                "$dateToString": {
                    "format": "%Y-%m",
                    "date": "$post_time"
                }
            },
        }
    }, {
        "$group": {
            "_id": "$post_time",
            "count": {
                "$sum": 1
            }
        }
    }, {
        "$project": {
            "name": {
                "$dateFromString": {
                    "dateString": "$_id",
                }
            },
            "value": {
                "$abs": "$count"
            },
        }
    }, {
        "$sort": {
            "_id": 1
        }
    }

    ], allowDiskUse=True)
    res = []
    for row in records:
        del row["_id"]
        row["name"] = row["name"].strftime('%Y-%m')
        res.append(row)
    redisConn.set("earthquake_macroscopic_bar1", res)
    res = {}
    countTotal = db.posts.find({
        "task": task,
        "label": "1"
    }).count()
    countEvent = DisasterInfo.objects.filter(task=task).count()
    res['countTotal'] = countTotal
    res['countEvent'] = countEvent
    redisConn.set("earthquake_macroscopic_basestatistics", res)
    return HttpResponse("缓存更新成功")

