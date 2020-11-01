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

import jieba
from django.db import connection
from django.http import HttpResponse

from ..models import PostExtra
stopwords_path = os.path.join(os.path.dirname(__file__),"resources", "stop_words.txt")
stopwords = [line.strip() for line in open(stopwords_path, 'r', encoding='utf-8').readlines()]
# 列出具体某次灾害的微博文本
def list1(request):
    number = request.GET.get("number", -1)
    cursor = connection.cursor()
    sql = f"SELECT post_content,comment_num,like_num,forward_num,post_time,user_id,b.post_id FROM post_extra as a,weibo_post as b where a.task_id=b.task_id and a.post_id=b.post_id and cluster = {number} order by post_time desc;"
    cursor.execute(sql)
    records = cursor.fetchall()
    res = []
    for row in records:
        # content = re.sub("<#>|</#>|<@>.*?</@>|<u>.*?</u>|#", '', row[0])
        res.append({
            'post_time': row[4].strftime('%Y-%m-%d %H:%M:%S'),
            'forward_num': row[3],
            'comment_num': row[1],
            'like_num': row[2],
            'post_content': re.sub("<#>|</#>|<@>.*?</@>|<u>.*?</u>", '',row[0]),
            'post_url': "https://weibo.com/" + str(row[5]) + "/" + str(row[6]) + "/"
        })
    res = {
        "code": 200,
        "msg": "success",
        "totalCount": len(res),
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 列出具体某次灾害的微博词云
def wordcloud1(request):
    number = request.GET.get("number", -1)
    cursor = connection.cursor()
    sql = f"SELECT post_content FROM post_extra as a,weibo_post as b where a.task_id=b.task_id and a.post_id=b.post_id and cluster = {number};"
    cursor.execute(sql)
    records = cursor.fetchall();
    word_count_list = []
    for row in records:
        content = str(row[0])
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
# 未对接
# 列出具体某次灾害的话题词云
def topiccloud1(request):
    number = request.GET.get("number", -1)
    cursor = connection.cursor()
    sql = f"SELECT post_content FROM post_extra as a,weibo_post as b where a.task_id=b.task_id and a.post_id=b.post_id and cluster = {number};"
    cursor.execute(sql)
    records = cursor.fetchall()
    topic_count_list = []
    for row in records:
        content = str(row[0])
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
    cursor = connection.cursor()
    # SELECT user_id,post_time,repost_id FROM post_extra as a,weibo_post as b where a.task_id=b.task_id and a.post_id=b.post_id and cluster = 1 order by post_time
    sql = f"SELECT post_time,repost_id FROM post_extra as a,weibo_post as b where a.task_id=b.task_id and a.post_id=b.post_id and cluster={number} order by post_time;"
    cursor.execute(sql)
    records = cursor.fetchall()
    post_num = len(records)
    re_num = 0
    num = 0
    begin_time = records[0][0]
    end_time = records[-1][0]
    print(begin_time)
    print(end_time)
    for row in records:
        if row[1] != None or row[1] != "-100":
            re_num += 1
        else:
            num += 1

    sql = f"select authentication from weibo_user where user_id in (SELECT user_id FROM post_extra as a,weibo_post as b where a.task_id=b.task_id and a.post_id=b.post_id and cluster={number} order by post_time);"
    cursor.execute(sql)
    records = cursor.fetchall()
    authority_num = 0
    user_num = len(records)
    for row in records:
        if row[0] == '1':
            authority_num += 1
    res = {
        "code": 200,
        "msg": "success",
        "data":{
            "totalCount": post_num,  # 帖子总数量
            "userCount": user_num,  # 用户数量
            "begin_time": begin_time.strftime('%Y-%m-%d %H:%M:%S'),  # 第一条帖子时间
            "end_time": end_time.strftime('%Y-%m-%d %H:%M:%S'),  # 最后一条帖子时间
            "originalCount": num,  # 原创帖子数量
            "forwardCount": re_num,  # 转发帖子的数量
            "authority_num": authority_num,  # 认证用户的数量
        }
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 热度走势展示
def heattrend1(request):
    number = int(request.GET.get("number", -1))
    cursor = connection.cursor()
    sql = f"select DATE_FORMAT(post_time,'%Y-%m-%d'),log(sum(forward_num)*0.4 + sum(comment_num)*0.4 + sum(like_num)*0.2+1) from post_extra as a,weibo_post as b where a.task_id=b.task_id and a.post_id=b.post_id and cluster = {number} group by DATE_FORMAT(post_time,'%Y-%m-%d');"
    cursor.execute(sql)
    records = cursor.fetchall()
    res = []
    for row in records:
        res.append({
            "time": row[0],# 时间，几时
            "heatCount": row[1] # 热度
        })
    res = {
        "code": 200,
        "msg": "success",
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
# 未对接
# 发帖地分布
def postlocmap1(request):
    number = int(request.GET.get("number", -1))
    cursor = connection.cursor()
    sql = f"select  province,count(*) from post_extra as a,weibo_post as b,weibo_user as c where a.task_id=b.task_id and a.post_id=b.post_id and b.user_id = c.user_id and cluster = {number} group by province;"
    cursor.execute(sql)
    records = cursor.fetchall()
    res = []
    for row in records:
        if row[0] == "-100":
            continue
        res.append({
            "name": row[0],# 时间，几时
            "value": row[1] # 热度
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
