# -*- coding: utf-8 -*-

#import time
#import sys
#from datetime import timedelta, datetime, date

import settings

from core.db import models
# from playhouse.db_url import connect
from core.hack_peewee import connect
#from core.exceptionutil import full_stack
import logging


# 异步service
#if TASKQUEUE_ENABLED:
#	from .tasks import send_watchdog

__author__ = 'chuter, victor, bert'

if settings.MODE == 'develop':
	WATCHDOG_DB = settings.DATABASES['default']
else:
	WATCHDOG_DB = settings.DATABASES['watchdog']

DB_URL = '%s://%s:%s@%s/%s' % (WATCHDOG_DB['ENGINE'], WATCHDOG_DB['USER'], WATCHDOG_DB['PASSWORD'], \
	"%s:%s" % (WATCHDOG_DB['HOST'], WATCHDOG_DB['PORT']) if len(WATCHDOG_DB['PORT'])>0 else WATCHDOG_DB['HOST'], WATCHDOG_DB['NAME'])
watchdog_db = connect(DB_URL)
watchdog_db.connect()

#信息等级
#全部
WATCHDOG_ALL = 0
#DEBUG级别
#例如记录收到请求中的参数信息等等
WATCHDOG_DEBUG = 100
#INFO级别，用于记录系统的实际行为，谁在什么时候对什么资源做了什么操作
WATCHDOG_INFO = 200
#不健康的现象，用户不可见，不会对系统产生影响，但是需要注意, 可能是一些问题的先兆
#例如请求微信api失败，重试后能成功这样的信息需要留意，可能网络有问题等等
WATCHDOG_NOTICE = 300
#操作失败，用户可见，会进行自动恢复，最终系统会一致，需要进行警告，
#便于研发人员进行整理发现问题，避免出现较大的问题
#例如获取微信用户的头像和昵称失败，只会影响到运营人员单个账号，
#而且这样的操作会请求微信api, 失败的因素有很多（系统有容错机制，
#最终会保证终端用户能看到正确的数据）
WATCHDOG_WARNING = 400
#系统出错，但是只影响当次请求的单个用户，对处理速度的要求没有那么高，
#而且通过重试或稍后自动或人工干预就可恢复
#例如由于授权过期或网络问题导致发送消息失败，而发送消息不是我们系统的最核心功能
#又例如用户传入的参数非法等等
WATCHDOG_ERROR = 500
#系统出错，只影响当次请求的单个用户，但比较严重，不会自动恢复，或者是
#系统的核心功能
#例如某一终端用户下单失败，又或者某一用户的消息没能进行自动回复等
WATCHDOG_FATAL = 600
#系统故障，会影响在线的所有终端用户，需要立刻处理
#例如所有消息无法进行自动回复，或者所有商城不能下订单不能支付，又或者微站访问报错
WATCHDOG_ALERT = 700
#最高级别的故障，整个系统不可使用
#例如502
WATCHDOG_EMERGENCY = 900
		
SEVERITIES = (
	(WATCHDOG_ALL, '全部'),
	(WATCHDOG_DEBUG, 'DEBUG'),
	(WATCHDOG_INFO, 'INFO'),
	(WATCHDOG_NOTICE, 'NOTICE'),
	(WATCHDOG_WARNING, 'WARNING'),
	(WATCHDOG_ERROR, 'ERROR'),
	(WATCHDOG_FATAL, 'FATAL'),
	(WATCHDOG_ALERT, 'ALERT'),
	(WATCHDOG_EMERGENCY, 'EMERGENCY')
)


class Message(models.Model):
	"""
	对运行时产生的log信息的封装
	"""
	user_id = models.CharField(default='0', max_length=50) #微站拥有者id
	severity = models.IntegerField(choices=SEVERITIES, db_index=True)
	type = models.CharField(max_length=50)
	message = models.TextField()
	create_time = models.DateTimeField(auto_now_add=True)
	
	#TODO 根据数据量是否需要使用mongodb？
	#是否需要针对不同级别进行分开存储？
	# def save(self, *args, **kwargs):
	# 	if self.user_id is None:
	# 		self.user_id = '0'

	# 	if settings.WATCH_DOG_DEVICE == 'mysql':
	# 		self.save_base(*args, **kwargs)
	# 	else:
	# 		pass
	
	class Meta(object):
		db_table = 'weapp_watchdog_message'
		verbose_name = '运维日志'
		verbose_name_plural = '运维日志'
		database = watchdog_db


class WeappMessage(models.Model):
	"""
	对运行时产生的log信息的封装
	"""
	user_id = models.CharField(default='0', max_length=50) #微站拥有者id
	severity = models.IntegerField(choices=SEVERITIES, db_index=True)
	type = models.CharField(max_length=50)
	message = models.TextField()
	create_time = models.DateTimeField(auto_now_add=True)
	
	#TODO 根据数据量是否需要使用mongodb？
	#是否需要针对不同级别进行分开存储？
	def save(self, *args, **kwargs):
		if self.user_id is None:
			self.user_id = '0'

		if settings.WATCH_DOG_DEVICE == 'mysql':
			self.save_base(*args, **kwargs)
		else:
			pass
	
	class Meta(object):
		db_table = 'weapp_watchdog_message'
		verbose_name = '运维日志'
		verbose_name_plural = '运维日志'
		ordering = ["-create_time"]




"""
`watchdog.models.watchdog_*` 已被废弃，用 `watchdog.util.watchdog_*`
"""
#import watchdog.utils as watchdog_util
def show_deprecation(name):
	def inner_func():
		print("NOTICE: 'watchdog.models.{}' was deprecated. Use 'watchdog.utils.{}' instead.", name, name)
	return inner_func
watchdog_info = show_deprecation("watchdog_info")
watchdog_warning = show_deprecation("watchdog_info")
watchdog_debug = show_deprecation("watchdog_debug")
watchdog_fatal = show_deprecation("watchdog_fatal")
watchdog_error = show_deprecation("watchdog_error")
watchdog_alert = show_deprecation("watchdog_alert")
watchdog_emergency = show_deprecation("watchdog_emergency")
watchdog_notice = show_deprecation("watchdog_notice")
#watchdog_info = watchdog_util.watchdog_info
#watchdog_warning = watchdog_util.watchdog_warning
#watchdog_debug = watchdog_util.watchdog_debug
#watchdog_fatal = watchdog_util.watchdog_fatal
#watchdog_error = watchdog_util.watchdog_error
#watchdog_alert = watchdog_util.watchdog_alert
#watchdog_emergency = watchdog_util.watchdog_emergency
#watchdog_notice = watchdog_util.watchdog_notice

