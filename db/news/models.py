# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from datetime import datetime
import json
import time

from core.db import models
from db.account.models import User, UserProfile



#########################################################################
# Material：素材
#########################################################################
SINGLE_NEWS_TYPE = 1
MULTI_NEWS_TYPE = 2
MATERIAL_TYPES = (
    (SINGLE_NEWS_TYPE, '单图文消息'),
    (MULTI_NEWS_TYPE, '多图文消息')
)
class Material(models.Model):
    owner = models.ForeignKey(User, related_name='owned_materials')
    type = models.IntegerField(default=SINGLE_NEWS_TYPE, choices=MATERIAL_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False) #是否删除

    class Meta(object):
        db_table = 'material_material'
        verbose_name = '素材'
        verbose_name_plural = '素材'


#########################################################################
# News：一条图文消息
#########################################################################
class News(models.Model):
    material = models.ForeignKey(Material) #素材外键
    display_index = models.IntegerField() #显示顺序
    title = models.CharField(max_length=40) #标题
    summary = models.CharField(max_length=120) #摘要
    text = models.TextField(default='') #正文
    pic_url = models.CharField(max_length=1024) #图片url地址
    url = models.CharField(max_length=1024) #目标地址
    link_target = models.CharField(max_length=2048) #链接目标
    is_active = models.BooleanField(default=True) #是否启用
    created_at = models.DateTimeField(auto_now_add=True) #添加时间
    is_show_cover_pic = models.BooleanField(default=True, verbose_name=u"是否在详情中显示封面图片")

    class Meta(object):
        db_table = 'material_news'
        verbose_name = '图文消息'
        verbose_name_plural = '图文消息'