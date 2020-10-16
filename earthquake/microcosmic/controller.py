#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/23 17:03
# @Author  : hui
# @Email   : huihuil@bupt.edu.cn
# @File    : controller.py
import collections
import json
import os
from typing import re

import jieba
from django.db import connection
from django.http import HttpResponse

from ..models import PostExtra
stopwords = os.path.abspath(__file__)
# 列出具体某次灾害的微博文本
def list1(request):
    number = request.GET.get("number", -1)
    cursor = connection.cursor()
    sql = f"SELECT post_content,comment_num,like_num,forward_num,post_time FROM post_extra as a,weibo_post as b where a.task_id=b.task_id and a.post_id=b.post_id and cluster = {number};"
    cursor.execute(sql)
    records = cursor.fetchall();
    res = []
    for row in records:
        res.append({
            'post_time': row[4].strftime('%Y-%m-%d %H:%M:%S'),
            'forward_num': row[3],
            'comment_num': row[1],
            'like_num': row[2],
            'post_content': row[0]
        })
    res = {
        "code": 200,
        "msg": "success",
        "totalCount": 1000,
        "data": res
    }
    res = json.dumps(res, ensure_ascii=False)
    return HttpResponse(res)
def wordcloud1(request):
    number = request.GET.get("number", -1)
    cursor = connection.cursor()
    sql = f"SELECT post_content,comment_num,like_num,forward_num,post_time FROM post_extra as a,weibo_post as b where a.task_id=b.task_id and a.post_id=b.post_id and cluster = {number};"
    cursor.execute(sql)
    records = cursor.fetchall();
    res = []
    for row in records:
        content = str(row[0])
        if len(content) >= 5:
            # 分词与词性标注
            content = re.sub("<#>|</#>|<@>.*?</@>|<u>.*?</u>|#", '', content)
            words = jieba.cut(content, cut_all=False, HMM=True)
            for word in words:
                if len(word) > 1 and re.match('[^\u4e00-\u9fa5]', word) == None and word not in stopwords:
                    word_count_list.append(word)
    word_counts = collections.Counter(word_count_list)
    data = []
    for k,v,in word_counts.most_common(50):
        data.append({
            'name':k,
            'value':v
        })