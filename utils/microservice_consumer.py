# -*- coding: utf-8 -*-
import json

import requests

from core.exceptionutil import unicode_full_stack
from core.watchdog.utils import watchdog_alert

DEFAULT_TIMEOUT = 5  # 默认超时时间单位：秒
DEFAULT_RETRY_COUNT = 3  # 重试次数


# 非200状态码
class ResponseCodeException(Exception):
	pass


class MicroserviceConsumer(object):
	pass


def conn_try_again(function):
	RETRIES = 0
	# 重试的次数
	count = {"num": RETRIES}

	def wrapped(*args, **kwargs):
		try:
			return function(*args, **kwargs)
		except Exception as e:
			if count['num'] < DEFAULT_RETRY_COUNT:
				count['num'] += 1
				return wrapped(*args, **kwargs)
			else:
				return False, None

	return wrapped


@conn_try_again
def microservice_consume(url='', data={}, method='get', timeout=None):
	_timeout = timeout if timeout else DEFAULT_TIMEOUT
	try:
		if method == 'get':
			resp = requests.get(url, data, timeout=_timeout)
		elif method == 'post':
			resp = requests.post(url, data, timeout=_timeout)
		else:
			# 兼容架构中的put、delete方法
			url = url + '?_method=' + method if '_method' not in url else url
			resp = requests.post(url, data, timeout=_timeout)
		if resp.status_code == 200:
			resp_data = json.loads(resp.text)['data']
			return True, resp_data
		else:
			watchdog_alert(u'外部接口调用错误-错误状态码.code:%s,url:%s，data:%s' % (resp.status_code, url, str(data)))
			raise ResponseCodeException
	except BaseException as e:
		traceback = unicode_full_stack()
		watchdog_alert(u'外部接口调用错误-异常.url:%s,msg:%s,url:%s ,data:%s' %  (url, traceback, url, str(data)))
		raise Exception(e)

# 测试代码
# url = 'http://dev.weapp.com/m/apps/group/api/group_buy_product?pid=48&woid=63'
# param_data = {'pid': '48', 'woid': '63'}
# is_success, group_buy_product = microservice_consume(url=url, data=param_data)
# print('--------is_success',is_success)
# print('group_buy_product',group_buy_product)
