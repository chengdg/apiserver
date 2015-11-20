#coding:utf8
from __future__ import absolute_import

import settings
from core.exceptionutil import full_stack

from apiserver.celery import task
from .models import Message, WeappMessage
from .models import WATCHDOG_ALERT,WATCHDOG_DEBUG,WATCHDOG_EMERGENCY,WATCHDOG_ERROR,WATCHDOG_FATAL,WATCHDOG_INFO,WATCHDOG_NOTICE,WATCHDOG_WARNING


def _watchdog(type, message, severity=WATCHDOG_INFO, user_id='0', db_name='default'):
	"""
	watchdog : 向日志记录表添加一条日志信息
	"""
	#try:
	if isinstance(user_id, int):
		user_id = str(user_id)

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
				print "[%s] [%s] : %s" % (severity, type, message)
			Message.create(type=type, message=message, severity=severity, user_id=user_id)
		except:
			print "Cause:\n{}".format(full_stack())
			print 'error message==============', message
			Message.create(type=type, message=message, severity=severity, user_id=user_id)


#取消无限制重试
@task(bind=True, max_retries=3)
def send_watchdog(self, level, message, severity=WATCHDOG_INFO, user_id='0', db_name='default'):
	try:
		if not settings.IS_UNDER_BDD:
			print 'received watchdog message: [%s] [%s]' % (level, message)
		_watchdog(level, message, severity, user_id, db_name)
	except:
		print "Failed to send watchdog message, retrying.:Cause:\n{}".format(full_stack())
		raise self.retry()
	return 'OK'
