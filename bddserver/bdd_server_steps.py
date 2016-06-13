# coding:utf8
# bdd server相关的step

import base64
import decimal
import json
import os
from cgi import parse_qs
from datetime import datetime, date
from wsgiref.simple_server import WSGIRequestHandler, make_server
from wsgiref.util import setup_testing_defaults
from features import environment

from behave import *

try:
	import settings
except ImportError:
	from django.conf import settings
except:
	raise ImportError('bdd_server import setting error.')

if not hasattr(settings, 'BDD_SERVER2PORT'):
	from weapp import settings

	assert hasattr(settings, 'BDD_SERVER2PORT'), 'BDD_SERVER2PORT import error!'

BDD_SERVER2PORT = settings.BDD_SERVER2PORT

BDD_SERVER_HOST = '127.0.0.1'


def full_stack():
	import traceback, sys
	exc = sys.exc_info()[0]
	stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
	if not exc is None:  # i.e. if an exception is present
		del stack[-1]  # remove call of full_stack, the printed exception
		# will contain the caught exception caller instead
	trc = 'Traceback (most recent call last, REVERSED CALL ORDER):\n'
	stackstr = trc + ''.join(reversed(traceback.format_list(stack)))
	if not exc is None:
		stackstr += '  ' + traceback.format_exc().lstrip(trc)

	return stackstr


def unicode_full_stack():
	return full_stack().decode('utf-8')


def _default(obj):
	if isinstance(obj, datetime):
		return obj.strftime('%Y-%m-%d %H:%M:%S')
	elif isinstance(obj, date):
		return obj.strftime('%Y-%m-%d')
	elif isinstance(obj, decimal.Decimal):
		return str(obj)
	else:
		return ''


def _set_context_attrs(context, context_kvs):
	for k, v in context_kvs.items():
		if v:
			setattr(context, k, v)


def _git_shell(git_command):
	try:
		return os.popen(git_command).read().strip()
	except:
		return None


# 获得本BDD_SERVER名称
try:
	current_path = os.path.split(os.path.realpath(__file__))[0]
	self_name = current_path.split(os.sep)[-2]
except BaseException as e:
	print(e)
	self_name = "BDD_SERVER name error!"
	print(self_name)


class BDDRequestHandler(WSGIRequestHandler):
	def handle(self):
		WSGIRequestHandler.handle(self)

		if 'shutdown=1' in self.raw_requestline:
			import threading
			threading.Thread(target=self.shutdown_server()).start()

	def shutdown_server(self):
		server = self.server

		def inner_shutdown():
			server.shutdown()
			server.server_close()
			print('[bdd server] server is shutdown now!')

		return inner_shutdown


@given(u'启动BDD Server')
def step_impl(context):
	# A relatively simple WSGI application. It's going to print(out the)
	# environment dictionary after being updated by setup_testing_defaults
	def simple_app(environ, start_response):

		# 修改窗口名,目前只对windows有效
		try:
			os.system("title {}_bdd_server".format(self_name))
		except:
			pass

		setup_testing_defaults(environ)

		status = '200 OK'
		headers = [('Content-type', 'text/plain')]

		start_response(status, headers)

		# the environment variable CONTENT_LENGTH may be empty or missing
		try:
			request_body_size = int(environ.get('CONTENT_LENGTH', 0))
		except (ValueError):
			request_body_size = 0

		# When the method is POST the query string will be sent
		# in the HTTP request body which is passed by the WSGI server
		# in the file like wsgi.input environment variable.
		# 从http request解析请求
		request_body = environ['wsgi.input'].read(request_body_size)
		post = parse_qs(request_body)
		step_data = json.loads(post['data'][0])
		step = step_data['step'].strip()

		# 1. 解析step
		# 2. 执行step
		# 3. 分类step执行结果
		# 4. 返回http response

		# 0:成功，1：业务失败，2：异常
		result = 0
		if step == '__reset__':
			print('*********************** run step **********************')
			print(u'Reset bdd environment...')
			environment.after_scenario(context, context.scenario)
			environment.before_scenario(context, context.scenario)

			resp = {
				'result': result,
				'bdd_server_name': self_name
			}

			return base64.b64encode(json.dumps(resp))
		else:
			# 解析请求携带的context
			_set_context_attrs(context, json.loads(step_data['context_attrs']))

			if step_data['context_text']:
				step_content = step_data['context_text']
			else:
				step_content = step_data['context_table']
			step = u'%s\n"""\n%s\n"""' % (step_data['step'], step_content)
			print('*********************** run step **********************')
			print(step)

			context_attrs = {}
			traceback = ''

			try:
				context.execute_steps(step)
			except AssertionError:
				result = 1
				print('*********************** failure **********************')
				traceback = full_stack()
				print(traceback.decode('utf-8'))

			except:
				result = 2
				print('*********************** exception **********************')
				traceback = full_stack()
				print(traceback.decode('utf-8'))

			else:
				result = 0
				context_attrs = context._stack[0]

			resp = {
				'result': result,
				'traceback': traceback,
				'context_attrs': context_attrs,
				'bdd_server_name': self_name
			}

			# 传递context时忽略基本类型外的对象
			return base64.b64encode(json.dumps(resp, default=_default))

	port = BDD_SERVER2PORT.get(self_name, 0)
	assert port, "{} is not valid name.You can't change the git repository name!".format(self_name)

	# 启动服务器
	httpd = make_server('', port, simple_app, handler_class=BDDRequestHandler)
	print("[{} bdd server] Serving on port {}...".format(self_name, port))
	httpd.serve_forever()
