#coding:utf8
from __future__ import absolute_import

import settings
from core.exceptionutil import full_stack
import logging

from core.service.celery import task
from .mongo_watchdog import MongoWatchdog
from .mysql_watchdog import MySQLWatchdog
from .models import WATCHDOG_ALERT,WATCHDOG_DEBUG,WATCHDOG_EMERGENCY,WATCHDOG_ERROR,WATCHDOG_FATAL,WATCHDOG_INFO,WATCHDOG_NOTICE,WATCHDOG_WARNING

_watchdog_logger = None

def _watchdog(type, message, severity=WATCHDOG_INFO, user_id='0', db_name='default'):
	"""
	watchdog : 向日志记录表添加一条日志信息
	"""
	#try:
	if isinstance(user_id, int):
		user_id = str(user_id)

	global _watchdog_logger
	if _watchdog_logger is None:
		#_watchdog_logger = MongoWatchdog()
		_watchdog_logger = MySQLWatchdog()
		logging.info(u'using {} as watchdog_logger'.format(_watchdog_logger))

	if settings.WATCH_DOG_DEVICE == 'console':
		if severity == WATCHDOG_DEBUG:
			severity = 'DEBUG'
		elif severity == WATCHDOG_INFO:
			severity = 'INFO'
		elif severity == WATCHDOG_NOTICE:
			severity = 'NOTICE'
		elif severity == WATCHDOG_WARNING:
			severity = 'WARNING'
		elif severity == WATCHDOG_ERROR:
			severity = 'ERROR'
		elif severity == WATCHDOG_FATAL:
			severity = 'FATAL'
		elif severity == WATCHDOG_ALERT:
			severity = 'ALERT'
		elif severity == WATCHDOG_EMERGENCY:
			severity = 'EMERGENCY'
		else:
			severity = 'UNKNOWN'
	else:
		try:
			if not settings.IS_UNDER_BDD:
				logging.info("WATCHDOG: [%s] [%s] : %s" % (severity, type, message))
			#Message.create(type=type, message=message, severity=severity, user_id=user_id)
			detail = message
			_watchdog_logger.log(severity, type, message, detail, user_id)
		except:
			logging.error("Cause:\n{}".format(full_stack()))
			logging.error('error message=============={}'.format(message))
			#Message.create(type=type, message=message, severity=severity, user_id=user_id)



#取消无限制重试
@task(bind=True, max_retries=3)
def send_watchdog(self, type, message, severity=WATCHDOG_INFO, user_id='0', db_name='default'):
	try:
		if not settings.IS_UNDER_BDD:
			logging.info(u'received watchdog message: [%s] [%s]' % (type, message))
		_watchdog(type, message, severity, user_id, db_name)
	except:
		print "Failed to send watchdog message, retrying.:Cause:\n{}".format(full_stack())
		raise self.retry()
	return 'OK'
