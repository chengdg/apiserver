#coding: utf8
"""@package db.third_party_pay.models
第三方支付存储模型
"""

from eaglet.core.db import models
from db.account.models import User


class JinGeCard(models.Model):
	"""
	锦歌公司饭卡
	"""
	owner = models.ForeignKey(User)
	member_id = models.IntegerField() #会员id
	phone_number = models.CharField(max_length=11)  #手机号
	card_number = models.CharField(max_length=20, default='')  #卡号
	card_password = models.CharField(max_length=256, default='')  #RSA加密后的密码
	token = models.CharField(max_length=256, default='')  #用户在饭卡数据系统中的身份标识
	name = models.CharField(max_length=32)  #持卡人姓名
	company = models.CharField(max_length=64)  #持卡人公司名称
	is_deleted = models.BooleanField(default=False) #是否删除/解绑
	created_at = models.DateTimeField(auto_now_add=True) #添加时间

	class Meta(object):
		db_table = 'third_party_jinge_card'
		verbose_name = '锦歌公司饭卡'
		verbose_name_plural = '锦歌公司饭卡'


class JinGeCardLog(models.Model):
	"""
	锦歌饭卡交易记录
	"""
	jinge_card = models.ForeignKey(JinGeCard)  #jinge card id
	price = models.FloatField(default=0.0)  # 浮动金额
	trade_id = models.CharField(max_length=50, default='') #支付流水号
	order_id = models.CharField(max_length=32, default='') #订单号
	reason = models.CharField(max_length=128)  # 原因
	created_at = models.DateTimeField(auto_now_add=True) #时间
	
	class Meta(object):
		db_table = 'third_party_jinge_card_log'
		verbose_name = '锦歌公司饭卡交易记录'
		verbose_name_plural = '锦歌公司饭卡交易记录'