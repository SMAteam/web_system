#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/10/21 9:51
# @Author  : hui
# @Email   : huihuil@bupt.edu.cn
# @File    : serializer.py.py
# 序列化
from django.contrib.auth.models import User,Group
from  rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model =Group
        fields = "__all__"