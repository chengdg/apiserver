# -*- coding: utf-8 -*-

#coding:utf8
"""@package weapp.watchdog.utils

Watchdog接口
"""

import settings
import sys

from core.service import celeryconfig
from models import *

from tasks import _watchdog, send_watchdog

__author__ = 'victor'

DEFAULT_WATCHDOG_TYPE = 'APISERVER'

def watchdog_debug(message, type=DEFAULT_WATCHDOG_TYPE, user_id='0', db_name='default'):
	"""
	用异步方式发watchdog

	异步方式调用 weapp.services.send_watchdog_service.send_watchdog()
	"""
	result = None
	if not celeryconfig.CELERY_ALWAYS_EAGER:
		if WATCHDOG_DEBUG >= settings.WATCH_DOG_LEVEL:
			result = send_watchdog.delay(type, message, WATCHDOG_DEBUG, user_id, db_name)
	else:
		if WATCHDOG_DEBUG >= settings.WATCH_DOG_LEVEL:
			_watchdog(type, message, WATCHDOG_DEBUG, user_id, db_name)
	return result
	#print message


def watchdog_info(message, type=DEFAULT_WATCHDOG_TYPE, user_id='0', db_name='default'):
	"""
	用异步方式发watchdog

	异步方式调用 weapp.services.send_watchdog_service.send_watchdog()
	"""
	result = None
	if not celeryconfig.CELERY_ALWAYS_EAGER:
		if WATCHDOG_INFO >= settings.WATCH_DOG_LEVEL:
			result = send_watchdog.delay(type, message, WATCHDOG_INFO, user_id, db_name)
	else:
		if WATCHDOG_INFO >= settings.WATCH_DOG_LEVEL:
			_watchdog(type, message, WATCHDOG_INFO, user_id, db_name)	
	return result


def watchdog_notice(message, type=DEFAULT_WATCHDOG_TYPE, user_id='0', db_name='default'):
	"""
	用异步方式发watchdog

	异步方式调用 weapp.services.send_watchdog_service.send_watchdog()
	"""
	result = None
	if not celeryconfig.CELERY_ALWAYS_EAGER:
		if WATCHDOG_NOTICE>= settings.WATCH_DOG_LEVEL:
			result = send_watchdog.delay(type, message, WATCHDOG_NOTICE, user_id, db_name)
	else:
		if WATCHDOG_NOTICE >= settings.WATCH_DOG_LEVEL:
			_watchdog(type, message, WATCHDOG_NOTICE, user_id, db_name)
	return result


def watchdog_warning(message, type=DEFAULT_WATCHDOG_TYPE, user_id='0', db_name='default'):
	"""
	用异步方式发watchdog

	异步方式调用 weapp.services.send_watchdog_service.send_watchdog()
	"""
	result = None
	if not celeryconfig.CELERY_ALWAYS_EAGER:
		if WATCHDOG_WARNING>= settings.WATCH_DOG_LEVEL:
			result = send_watchdog.delay(type, message, WATCHDOG_WARNING, user_id, db_name)
	else:
		if WATCHDOG_NOTICE >= settings.WATCH_DOG_LEVEL:
			_watchdog(type, message, WATCHDOG_NOTICE, user_id, db_name)
	return result


def watchdog_error(message, type=DEFAULT_WATCHDOG_TYPE, user_id='0', noraise=False, db_name='default'):
	result = None
	if not celeryconfig.CELERY_ALWAYS_EAGER:
		if WATCHDOG_ERROR >= settings.WATCH_DOG_LEVEL:
			result = send_watchdog.delay(type, message, WATCHDOG_ERROR, user_id, db_name)
		if settings.DEBUG and (not noraise):
			exception_type, value, tb = sys.exc_info()
			if exception_type:
				raise exception_type, exception_type(value), sys.exc_info()[2]
	else:
		if WATCHDOG_ERROR >= settings.WATCH_DOG_LEVEL:
			_watchdog(type, message, WATCHDOG_ERROR, user_id, db_name)
		if settings.DEBUG and (not noraise):
			exception_type, value, tb = sys.exc_info()
			if exception_type:
				raise exception_type, exception_type(value), sys.exc_info()[2]
	return result


def watchdog_fatal(message, type=DEFAULT_WATCHDOG_TYPE, user_id='0', noraise=False, db_name='default'):
	result = None
	if not celeryconfig.CELERY_ALWAYS_EAGER:
		if WATCHDOG_FATAL >= settings.WATCH_DOG_LEVEL:
			send_watchdog.delay(type, message, WATCHDOG_FATAL, user_id, db_name)
		if settings.DEBUG and (not noraise):
			exception_type, value, tb = sys.exc_info()
			if exception_type:
				raise exception_type, exception_type(value), sys.exc_info()[2]
	else:
		if WATCHDOG_FATAL >= settings.WATCH_DOG_LEVEL:
			_watchdog(type, message, WATCHDOG_FATAL, user_id, db_name)
		if settings.DEBUG and (not noraise):
			exception_type, value, tb = sys.exc_info()
			if exception_type:
				raise exception_type, exception_type(value), sys.exc_info()[2]
	return result


def watchdog_alert(message, type=DEFAULT_WATCHDOG_TYPE, user_id='0', db_name='default'):
	result = None
	if not celeryconfig.CELERY_ALWAYS_EAGER:
		if WATCHDOG_ALERT >= settings.WATCH_DOG_LEVEL:
			send_watchdog.delay(type, message, WATCHDOG_ALERT, user_id, db_name)
	else:
		if WATCHDOG_ALERT >= settings.WATCH_DOG_LEVEL:
			_watchdog(type, message, WATCHDOG_ALERT, user_id, db_name)
	return result


def watchdog_emergency(message, type=DEFAULT_WATCHDOG_TYPE, user_id='0', db_name='default'):
	result = None
	if not celeryconfig.CELERY_ALWAYS_EAGER:
		if WATCHDOG_EMERGENCY >= settings.WATCH_DOG_LEVEL:
			send_watchdog.delay(type, message, WATCHDOG_EMERGENCY, user_id, db_name)
	else:
		if WATCHDOG_EMERGENCY >= settings.WATCH_DOG_LEVEL:
			_watchdog(type, message, WATCHDOG_EMERGENCY, user_id, db_name)
	return result
