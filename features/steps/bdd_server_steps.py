# coding:utf8
# bdd server相关的step

import base64
import json
from cgi import parse_qs
from wsgiref.simple_server import WSGIRequestHandler, make_server
from wsgiref.util import setup_testing_defaults
from features import environment

from behave import *

import settings


def get_context_attrs(context, *args, **kwargs):
	raw_context_kvs = context._stack[0]
	context_kvs = {}
	for k, v in raw_context_kvs.items():
		if isinstance(v, (basestring, int, float, list, dict, bool)):
			context_kvs[k] = v
	return context_kvs


def set_context_attrs(context, context_kvs):
	for k, v in context_kvs.items():
		setattr(context, k, v)


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
		request_body = environ['wsgi.input'].read(request_body_size)
		post = parse_qs(request_body)
		step_data = json.loads(post['data'][0])
		step = step_data['step'].strip()
		if step == '__reset__':
			print('*********************** run step **********************')
			print(u'重置bdd环境')
			environment.after_scenario(context, context.scenario)
			environment.before_scenario(context, context.scenario)
			return base64.b64encode('success')
		else:
			set_context_attrs(context, json.loads(step_data['context_kvs']))

			step = u'%s\n"""\n%s\n"""' % (step_data['step'], step_data['context_text'])
			print('*********************** run step **********************')
			print(step)

			try:
				context.execute_steps(u'%s\n"""\n%s\n"""' % (step_data['step'], step_data['context_text']))

				raw_context_kvs = context._stack[0]
				context_kvs = {}
				for k, v in raw_context_kvs.items():
					if isinstance(v, (basestring, int, float, list, dict, bool)) and k != 'text':
						try:
							tmp = {'a': v}
							json.dumps(tmp)
							context_kvs[k] = v
						except:
							print('%s,%s .can not json.loads' % (k, type(v)))
							pass
			except:
				from core.exceptionutil import full_stack
				print('*********************** exception **********************')
				stacktrace = full_stack()
				print(stacktrace.decode('utf-8'))
				return base64.b64encode(stacktrace)

			# return base64.b64encode('success')

			return base64.b64encode(json.dumps(context_kvs))

	httpd = make_server('', settings.BDD_SERVER_PORT, simple_app, handler_class=BDDRequestHandler)
	print("[bdd server] Serving on port {}...".format(settings.BDD_SERVER_PORT))
	httpd.serve_forever()
