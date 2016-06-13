# -*- coding: utf-8 -*-
"""
调用外部step
"""

# -*- coding: utf-8 -*-
import base64
import decimal
import json
from datetime import datetime, date

import requests
from behave import *


def full_stack():
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if not exc is None:  # i.e. if an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
        # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last, REVERSED CALL ORDER):\n'
    stackstr = trc + ''.join(reversed(traceback.format_list(stack)))
    if not exc is None:
        stackstr += '  ' + traceback.format_exc().lstrip(trc)

    return stackstr

def unicode_full_stack():
    return full_stack().decode('utf-8')

try:
	import settings
except ImportError:
	from django.conf import settings
except:
	raise ImportError('bdd_server import setting error.')

# BDD_SERVER2PORT = settings.BDD_SERVER2PORT
BDD_SERVER2PORT = {
    'weapp': 8170,
    'weizoom_card': 8171,
    'apiserver': 8172
}

_ignore_keys = ['scenario', 'tags', 'text', 'table', 'log_capture', 'client']


def _set_context_attrs(context, context_kvs):
	for k, v in context_kvs.items():
		if v and k not in _ignore_keys:
			setattr(context, k, v)


def _get_context_attrs():
	pass


def _default(obj):
	if isinstance(obj, datetime):
		return obj.strftime('%Y-%m-%d %H:%M:%S')
	elif isinstance(obj, date):
		return obj.strftime('%Y-%m-%d')
	elif isinstance(obj, decimal.Decimal):
		return str(obj)
	else:
		return ''


BDD_SERVER_HOST = '127.0.0.1'


def _run_bdd_server_step(step, context, bdd_server_name):
	port = BDD_SERVER2PORT.get(bdd_server_name)

	assert port, "不支持的bdd_server:{}".format(bdd_server_name)

	url = 'http://%s:%s' % (BDD_SERVER_HOST, port)
	if context:
		context_text = context.text
		context_table = context.table

		context_attrs = context._stack[0]
		context_attrs = json.dumps(context_attrs, default=_default)
	else:
		context_attrs = {}
		context_text = ''
		context_table = ''

	# 目前只传递context的属性、text、table
	data = {
		'step': step,
		'context_attrs': context_attrs,  # 忽略传递context中的对象
		'context_text': context_text,
		'context_table': context_table
	}

	response = requests.post(url, data={'data': json.dumps(data)})

	try:
		resp_data = json.loads(base64.b64decode(response.text.encode('utf-8')).decode('utf-8'))

		assert resp_data['bdd_server_name'].lower() == bdd_server_name.lower(), "Lv chun bu dui ma zui ERROR,call {},but get {}".format(bdd_server_name,resp_data['bdd_server_name'])

		result = int(resp_data['result'])
		# 一切正常
		if result == 0:
			if step != '__reset__':
				if resp_data['context_attrs']:
					_set_context_attrs(context, resp_data['context_attrs'])
		# 场景业务错误
		elif result == 1:
			buf = []
			buf.append('\n*************** START WEAPP STEP Failure ***************')
			buf.append(resp_data)
			buf.append('*************** FINISH WEAPP STEP Failure ***************\n')
			print(str(buf).decode('unicode-escape'))

			assert False, u'{} server业务校验失败'.format(bdd_server_name)
		# 发生异常
		elif result == 2:

			buf = []
			buf.append('\n*************** START WEAPP STEP Failure ***************')
			buf.append(resp_data)
			buf.append('*************** FINISH WEAPP STEP Failure ***************\n')
			print(buf)
			assert False, u'{} 外部server发生异常'.format(bdd_server_name)
		else:
			assert False, u'{}未定义的result'.format(result)
	except AssertionError as e:
		raise e

	except BaseException as e:
		print('***bdd_server exception***：', e)
		print('***bdd_server traceback***：', unicode_full_stack())

		assert False, u"BDD_SERVER:{}出错,无法解析".format(bdd_server_name)


@When(u"{command}::{bdd_server_name}")
def step_impl(context, command, bdd_server_name):
	_run_bdd_server_step(u'When %s' % command, context, bdd_server_name)


@Given(u"{command}::{bdd_server_name}")
def step_impl(context, command, bdd_server_name):
	_run_bdd_server_step(u'Given %s' % command, context, bdd_server_name)


@Then(u"{command}::{bdd_server_name}")
def step_impl(context, command, bdd_server_name):
	_run_bdd_server_step(u'Then %s' % command, context, bdd_server_name)


@given(u"重置'{}'的bdd环境")
def step_impl(context, bdd_server_name):
	_run_bdd_server_step('__reset__', None, bdd_server_name)
