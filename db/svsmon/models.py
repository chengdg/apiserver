# -*- coding: utf-8 -*-

#import time
#import sys
#from datetime import timedelta, datetime, date

from eaglet.core.db import models

__author__ = 'abael, bert'
__all__ = [
		'TASK_ACCEPTED',
		'TASK_REVOKED',
		'TASK_ERROR',
		'TASK_SUCCESS',
		'TASK_TIMEOUT',
		'TASK_RETRY',
		'TASK_FAILURE',
		'TASK_UNKNOWN',
		'Svsmon',
		]

TASK_ACCEPTED = 0 
TASK_SUCCESS  = 1 
TASK_REVOKED  = 2 
TASK_RETRY    = 3 
TASK_TIMEOUT  = 4 
TASK_FAILURE  = 5 
TASK_ERROR    = 6 
TASK_UNKNOWN  = 9 

TASK_STATUS = (
	(TASK_UNKNOWN, '未注册'),
	(TASK_ACCEPTED, '排号'),
	(TASK_REVOKED, '取消'),
	(TASK_ERROR, '错误'),
	(TASK_SUCCESS, '成功'),
	(TASK_TIMEOUT, '超时'),
	(TASK_RETRY, '重试'),
	(TASK_FAILURE, '失败'),
)
		
class Svsmon(models.Model):
	"""
	对运行时产生的log信息的封装
	"""
	task_id = models.CharField(blank=False, max_length=64, db_index=True)
	pid = models.IntegerField()
	status = models.IntegerField(default=TASK_STATUS, db_index=True)
	task = models.CharField(max_length=512)
	task_name = models.CharField(null=True, max_length=512) #
	message = models.TextField()
	create_time = models.DateTimeField(auto_now_add=True)
	
	#TODO 根据数据量是否需要使用mongodb？
	#是否需要针对不同级别进行分开存储？
	# def save(self, *args, **kwargs):
	# 	self.save_base(*args, **kwargs)
	
	class Meta(object):
		verbose_name = 'Celery日志'
		verbose_name_plural = 'Celery日志'
		#ordering = ['task_id', "-create_time", 'task']
