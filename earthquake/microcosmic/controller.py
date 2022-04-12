#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/23 17:03
# @Author  : hui
# @Email   : huihuil@bupt.edu.cn
# @File    : controller.py
import collections
import json
import os
import re
from ..models import DisasterInfo
import jieba
import pymongo
from django.http import HttpResponse
from py2neo import Graph
stopwords_path = os.path.join(os.path.dirname(__file__),"resources", "stop_words.txt")
stopwords = [line.strip() for line in open(stopwords_path, 'r', encoding='utf-8').readlines()]
client = pymongo.MongoClient(host = "localhost", port = 27017, maxPoolSize=50)
# graph = Graph(
#     "http://49.232.229.126:7474",
#     username="neo4j",
#     password="123456"
# )
graph = None
task = "1"
# 列出具体某次灾害的微博文本
def list1(request):
    number = int(request.GET.get("number", -1))
    if number == -1:
        number = DisasterInfo.objects.filter(task=task).order_by("number").last().number
    media = request.GET.get("media", "1")
    db = client.admin
    db.authenticate('root', 'buptweb007')
    db = client.SocialMedia
    records = db.Posts.find({
        "task": task,
        "media": str(media),
        "cluster": number
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
        "media": 1,
        "brief": 1,
        "label": 1
    })
    res = []
    for row in records:
        row["post_time"] = row["post_time"].strftime('%Y-%m-%d %H:%M:%S')
        if row["media"] == "1":
            row['post_content'] = re.sub("(<@>.*?</@>)|#|<#>|</#>|(<u>.*?</u>)", "", row['post_content'])
            # if "项目捐款成功" in row['post_content']:
            #     continue
        elif row["media"] == "2":
            row["post_content"] = row["brief"]
        res.append(row)
    if media == "2" and len(res) == 0:
        res.append({
            "title": "未找到相关新闻！",
            "post_content": "未找到相关新闻！",
            "post_time": "",
            "post_url": "",
            "like_num": "",
            "user_name": "",
            "forward_num": "",
            "comment_num": "",
            "media": "2",
        })
    res = {
        "code": 200,
        "msg": "success",
        "totalCount": len(res),
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 列出当地灾害史
def list2(request):
    number = int(request.GET.get("number", -1))
    if number == 859:
        db = client.admin
        db.authenticate('root', 'buptweb007')
        db = client.SocialMedia
        q = ["KgA2QzE3I", "KgAo3By77", "KgAMFsryJ", "KgAMxfrhs", "KgDXfmBJb", "KgF7DgscR", "KgF8s8d5H", "KgOTtF6rZ","KgX7rAI9F"]
        res = []
        tmp = []
        for i in q:
            records = db.Posts.find({
                "task": task,
                "media": "1",
                "cluster": number,
                "post_id": i,
            }, {
                "post_content": 1,
                "post_time": 1,
                "post_id": 1,
            })
            for r in records:
                tmp.append(r)

        for record in tmp:
            post_content = record.get("post_content", "")
            post_content = re.sub("(<@>.*?</@>)|#|<#>|</#>|(<u>.*?</u>)", "", post_content)
            post_id = record.get("post_id", "")
            post_time = record.get("post_time").strftime('%Y-%m-%d %H:%M')
            res.append({
                'number': 0,
                'province': "",
                'city': "",
                'area': post_time,
                'info': post_content,
                'time': "record.time.strftime('%Y-%m-%d %H:%M:%S')",
                'authority': 1,  # 可信度，1高可信度，0为低可信度
            })
        res = {
            "code": 200,
            "msg": "success",
            "province": "",
            "city": "",
            "totalCount": len(res),
            "data": res
        }
        res = json.dumps(res, ensure_ascii=False)
        return HttpResponse(res)
    if number == -1:
        number = DisasterInfo.objects.filter(task=task).order_by("number").last().number
    province = DisasterInfo.objects.filter(task=task, number=number).last().province
    city = DisasterInfo.objects.filter(task=task, number=number).last().city
    area = DisasterInfo.objects.filter(task=task, number=number).last().area
    if province != '-100':
        records = DisasterInfo.objects.filter(task=task, province=province).order_by("-time")
    if city != '-100':
        records = DisasterInfo.objects.filter(task=task, province=province, city=city).order_by("-time")
    if area != '-100':
        records = DisasterInfo.objects.filter(task=task, province=province, area=area).order_by("-time")
    res = []
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


# 列出具体某次灾害的微博词云
def wordcloud1(request):
    number = int(request.GET.get("number", -1))
    if number == -1:
        number = DisasterInfo.objects.filter(task=task).order_by("number").last().number
    db = client.admin
    db.authenticate('root', 'buptweb007')
    db = client.SocialMedia
    records = db.Posts.find({
        "task": task,
        "media": "1",
        "cluster": number
    }, {
        "post_content": 1,
    })
    word_count_list = []
    for row in records:
        content = str(row.get("post_content"))
        # if len(content) >= 0:
        # 分词与词性标注
        content = re.sub("<#>|</#>|<@>.*?</@>|<u>.*?</u>|#", '', content)
        words = jieba.cut(content, cut_all=False, HMM=True)
        for word in words:
            if len(word) > 1 and re.match('[^\u4e00-\u9fa5]', word) == None and word not in stopwords:
                word_count_list.append(word)
    word_counts = collections.Counter(word_count_list)

    res = []
    for k,v,in word_counts.most_common(100):
        res.append({
            'name':k,
            'value':v
        })
    res = {
        "code": 200,
        "msg": "success",
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 列出具体某次灾害的话题词云
def topiccloud1(request):
    number = int(request.GET.get("number", -1))
    if number == -1:
        number = DisasterInfo.objects.filter(task=task).order_by("number").last().number
    db = client.admin
    db.authenticate('root', 'buptweb007')
    db = client.SocialMedia
    records = db.Posts.find({
        "task": task,
        "media": "1",
        "cluster": number
    }, {
        "post_content": 1,
    })
    topic_count_list = []
    for row in records:
        content = str(row.get("post_content"))
        topics  = re.findall("<#>#(.*?)#</#>", content)
        for topic in topics:
            topic_count_list.append(topic)
    topic_counts = collections.Counter(topic_count_list)
    res = []
    for k, v, in topic_counts.most_common(100):
        res.append({
            'name': k,
            'value': v
        })
    res = {
        "code": 200,
        "msg": "success",
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 列出具体某次灾害的微博情况
def basestatistics1(request):
    number = int(request.GET.get("number", -1))
    if number == -1:
        obj = DisasterInfo.objects.filter(task=task).order_by("number").last()
        number = int(obj.number)
        province = obj.province
        city = obj.city if obj.city != "-100" else ""
        area = obj.area if obj.area != "-100" else ""
    else:
        obj = DisasterInfo.objects.filter(task=task, number=number).last()
        number = int(obj.number)
        province = obj.province
        city = obj.city if obj.city != "-100" else ""
        area = obj.area if obj.area != "-100" else ""
    db = client.admin
    db.authenticate('root', 'buptweb007')
    db = client.SocialMedia
    records = db.Posts.find({
        "task": task,
        "media": "1",
        "cluster": number
    })
    authorityCount = 0
    forwardCount = 0
    weiboCount = 0
    originalCount = 0
    userCount = set()
    weiboBeginTime = None
    for row in records:
        if weiboBeginTime == None:
            weiboBeginTime = row.get("post_time", None)
        weiboCount += 1
        if row.get("authentication", None) == "1":
            authorityCount += 1
        if row.get("repost_id", None) != None and row.get("repost_id", None) != "-100" and len(row.get("repost_id", None)) > 0:
            forwardCount += 1
        else:
            originalCount += 1
        if row.get("user_id", None) != None:
            userCount.add(row.get("user_id", None))
    userCount = len(userCount)
    records = db.Posts.find({
        "task": "1",
        "media": "2",
        "cluster": number
    })
    mediaCount = set()
    xinwenCount = 0
    xinwenBeginTime = None
    for row in records:
        if xinwenBeginTime == None:
            xinwenBeginTime = row.get("post_time", None)
        xinwenCount += 1
        if row.get("user_name", None) != None and row.get("user_name", None) != "-100" and len(row.get("user_name", None)) > 0:
            mediaCount.add(row.get("user_name", None))
    mediaCount = len(mediaCount)
    res = {
        "code": 200,
        "msg": "success",
        "weiboBeginTime": weiboBeginTime.strftime('%Y-%m-%d %H:%M:%S') if weiboBeginTime else None, # 微博中第一条帖子的发布时间
        "xinwenBeginTime": xinwenBeginTime.strftime('%Y-%m-%d %H:%M:%S') if xinwenBeginTime else None, # 新闻中第一条帖子的发布时间
        "data":{
            "weiboCount": weiboCount,  # 帖子总数量
            "userCount": userCount,  # 用户数量
            "originalCount": originalCount,  # 原创帖子数量
            "forwardCount": forwardCount,  # 转发帖子的数量
            "authorityCount": authorityCount,  # 认证用户的数量
            "xinwenCount": xinwenCount,
            "mediaCount": mediaCount,
            "province": province,
            "city": city,
            "area": area,
        }
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 热度走势展示
def heattrend1(request):
    number = int(request.GET.get("number", -1))
    if number == -1:
        number = DisasterInfo.objects.filter(task=task).order_by("number").last().number
    db = client.admin
    db.authenticate('root', 'buptweb007')
    db = client.SocialMedia
    date_format = "%Y-%m-%d"
    records = db.Posts.aggregate([{
        "$match": {
            "task": task,
            "media": "1",
            "cluster": number
        }
    }, {
        "$project": {
            "time": {
                "$dateToString": {
                    "format": date_format,
                    "date": "$post_time"
                }
            },
            "forwardNum": {
                "$abs": {
                    "$add":[ "$forward_num",1]
                }
            },
            "commentNum": {
                "$abs": {
                    "$add":[ "$comment_num",1]
                }
            },
            "likeNum": {
                "$abs": {
                    "$add":[ "$like_num",1]
                }
            },
        }
    }, {
        "$group": {
            "_id": "$time",
            "forwardSum": {
                "$sum": "$forwardNum"
            },
            "commentSum": {
                "$sum": "$commentNum"
            },
            "likeSum": {
                "$sum": "$likeNum"
            }
        }
    }, {
        "$project": {
            "time": {
                "$dateFromString": {
                    "dateString": "$_id",
                }
            },
            "heatCount": {
                "$add":[ {
                    "$multiply": [{
                        "$ln": [{"$add":["$forwardSum", 1]}]
                    }, 0.4] ,
                    "$multiply": [{
                        "$ln": [{"$add": ["$commentSum", 1]}]
                    }, 0.4],
                    "$multiply": [{
                        "$ln": [{"$add": ["$likeSum", 1]}]
                    }, 0.2],
                }]
            },
        }
    }, {
        "$sort": {
            "time": 1
        }
    }

    ])
    res = []
    for row in records:
        del row["_id"]
        row["time"] = row["time"].strftime(date_format)
        res.append(row)
    res = {
        "code": 200,
        "msg": "success",
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 发帖地分布
def postlocmap1(request):
    number = int(request.GET.get("number", -1))
    if number == -1:
        number = DisasterInfo.objects.order_by("number").last().number
    db = client.admin
    db.authenticate('root', 'buptweb007')
    db = client.SocialMedia
    pipeline = [
        {"$match": {"task": "1", "media": "1", "cluster": number}},
        {"$group": {"_id": "$province", "count": {"$sum": 1}}}
    ]
    records = db.Posts.aggregate(pipeline, allowDiskUse=True)
    res = []
    for row in records:
        if row.get("_id") != "海外" and row.get("_id") != "-100":
            res.append({
                "name": row.get("_id"),
                "value": int(row.get("count"))
            })
    res = {
        "code": 200,
        "msg": "success",
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 文本分类

# 情感分析

# 事件线
def eventline1(request):
    number = int(request.GET.get("number", -1))
    db = client.admin
    db.authenticate('root', 'buptweb007')
    db = client.SocialMedia
    pipeline = [
        {"$match": {"task": "1"}},
        {"$group": {"_id": "$cluster", "count": {"$sum": 1}}},
        {"$sort": {"count": 1}}
    ]
    records = db.Posts.aggregate(pipeline, allowDiskUse=True)
    res = []
    for row in records:
        res.append({
            "cluster": row.get("_id"),
            "value": int(row.get("count"))
        })
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)

# 知识图谱
def entitymatch(request):
    number = int(request.GET.get("number", -1))
    if number == -1:
        number = DisasterInfo.objects.filter(task=task).order_by("number").last().number
    province = DisasterInfo.objects.filter(task=task, number=number).last().province
    city = DisasterInfo.objects.filter(task=task, number=number).last().city
    time = DisasterInfo.objects.filter(task=task, number=number).last().time
    res = {
        "code": 200,
        "msg": "success",
    }
    if city == '-100':
        res["code"] = 404
        res['message'] = 'failed'
        res = json.dumps(res, ensure_ascii=False)
        return HttpResponse(res)
    name = province[:2] + city[:2] + '地震'
    time = time.strftime('%Y-%m-%d')
    matchN = f'MATCH (n:earthquake_entity) where n.name = "{name}" and n.time=~"{time}.*" return id(n) limit(1)'
    tmp = list(graph.run(matchN))
    if tmp == []:
        res["code"] = 404
        res['message'] = 'failed'
        res = json.dumps(res, ensure_ascii=False)
        return HttpResponse(res)
    entityID = tmp[0].values()[0]
    macth_str = f'MATCH (b2:earthquake_entity)-[r *1..2]->(n) where id(b2) = {entityID} RETURN r;'
    ret = list(graph.run(macth_str))
    ret = list(ret)
    tmp = set()
    for item in ret:
        try:
            tmp.add(item[0][0])
            tmp.add(item[0][1])
        except:
            continue
    Node = list()
    links = list()
    Node.append(name)
    res['message'] = 'success'
    for item in tmp:
        link = {}
        startNode = dict(item.start_node)['name']
        endNode = dict(item.end_node)['name']
        Node.append(startNode)
        Node.append(endNode)
        link['source'] = startNode
        link['target'] = endNode
        link['name'] = (type(item)).__name__
        links.append(link)
    data = {}
    Node = list(set(Node))
    Node.remove(name)
    Node.insert(0, name)
    data['node'] = []
    for i in Node:
        tmp = dict()
        tmp['name'] = i
        data['node'].append(tmp)
    data['links'] = links
    res['data'] = data
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
