# -*- coding: utf-8 -*-
import json

import requests

from core.exceptionutil import unicode_full_stack
from eaglet.core import watchdog

DEFAULT_TIMEOUT = 10  # 默认超时时间单位：秒
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
			try:
				weizoom_code = json.loads(resp.text)['code']
			except:
				weizoom_code = 10086  # 无法得到正确weizoom_code时的默认值
			if weizoom_code == 200:
				watchdog.info(u'microservice_consume_log,外部接口成功调用日志.code:%s,weizoom_code:%s,url:%s，request_data:%s,resp:%s' % (resp.status_code, weizoom_code,url, str(data),resp.text))
				return True, resp_data
			else:
				watchdog.alert(u'microservice_consume_alert,外部接口调用错误-wzcode错误状态码.code:%s,weizoom_code:%s,url:%s，request_data:%s,resp:%s' % (resp.status_code, weizoom_code,url, str(data),resp))
				raise ResponseCodeException
		else:
			watchdog.alert(u'microservice_consume_alert,外部接口调用错误-http错误状态码.code:%s,url:%s，data:%s' % (resp.status_code, url, str(data)))
			raise ResponseCodeException
	except BaseException as e:
		traceback = unicode_full_stack()
		watchdog.alert(u'外部接口调用错误-异常.url:%s,msg:%s,url:%s ,data:%s' %  (url, traceback, url, str(data)))
		raise Exception(e)

# 测试代码
# url = 'http://red.weapp.weizzz.com/m/apps/group/api/group_buy_product'
# # url = 'http://weapp.weizoom.com/m/apps/group/api/group_buy_products'
# param_data = {'pid': '48', 'woid': '9'}
# is_success, resp_data = microservice_consume(url=url, data=param_data)
# print('--------is_success',is_success)
# print('resp',resp_data)
