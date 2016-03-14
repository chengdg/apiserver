# -*- coding: utf-8 -*-
import json

import requests

from core.exceptionutil import unicode_full_stack
from core.watchdog.utils import watchdog_alert

DEFAULT_TIMEOUT = 3  # 单位：秒


class MicroserviceConsumer(object):
	pass


def microservice_consume(url='', data='', method='get', timeout=None):
	_timeout = timeout if timeout else DEFAULT_TIMEOUT
	try:

		if method == 'get':
			resp = requests.get(url, data, timeout=_timeout)
		elif method == 'post':
			print('---------------------------3')
			resp = requests.post(url, data, timeout=_timeout)
		else:
			# 兼容架构中的put、delete方法
			url = url + '?_method=' + method if '_method' not in url else url
			resp = requests.post(url, data, timeout=_timeout)
		if resp.status_code == 200:
			resp_data = json.loads(resp.text)['data']
			return True, resp_data
		else:
			print(u'外部接口调用错误-错误状态码.code:%s,url:%s', resp.status_code, url)
			watchdog_alert(u'外部接口调用错误-错误状态码.code:%s,url:%s', resp.status_code, url)
			return False, None
	except:
		traceback = unicode_full_stack()
		watchdog_alert(u'外部接口调用错误-异常.url:%s,msg:%s', url, traceback)
		print('----------------------------------------------------------------begin')
		print(traceback)
		print('----------------------------------------------------------------end')
		return False, None





