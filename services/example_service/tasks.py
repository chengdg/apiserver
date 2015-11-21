#coding:utf8
"""@package services.example_service.tasks
service示例
"""

#from watchdog.utils import watchdog_info
from celery import task

def some_other_func(request, args):
	"""
	其他不需要异步调用的函数
	"""
	print("in example_service.some_other_func()")
	print("request: {}".format(request))
	print("args: {}".format(args))
	return

@task
def example_log_service(request0, args):
	"""
	异步service示例

	调用方式：

		from services.example_service.tasks import example_log_service
		result = example_log_service.delay(None, request.event_data)
	"""
	# 构造request对象
	from services.service_manager import create_request
	request = create_request(args)

	print("log something: this is just a service example")
	# use (request, args) to do something
	some_other_func(request, args)
	return "OK"
