#coding: utf8
"""@package services.service_util
命令行方式启动Celery task

**用法**：

	python services/send_task.py <service_name> <arg> [<arg> ...]

**说明**：

	<service_name> : 服务的名称。如果在@task中指定name，则为次名字；否则为函数的全名。

**用法举例**：

	>python services\send_task.py watchdog.send 100 "This is a message"
	service name: watchdog.send
	args: ['100', 'Hello,  world!']
	result: OK

"""

import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#加载clery配置
from core.celery import celery
from core.celery import celeryconfig
celeryconfig.CELERY_ALWAYS_EAGER=False
if celeryconfig.CELERY_ALWAYS_EAGER:
	print("CELERY_ALWAYS_EAGER=True, use 'services.celery.send_task_test' instead")
	from services.celery_util import send_task_test as send_task
else:
	from celery.execute import send_task

if __name__=="__main__":
	if len(sys.argv)<3:
		print("usage: {} <service_name> <arg> [<arg> ...]".format(sys.argv[0]))
		print("example: {} watchdog.send 100 \"Hello, World!\"".format(sys.argv[0]))
		sys.exit(0)
	service_name = sys.argv[1]
	args = sys.argv[2:]
	print("service name: {}".format(service_name))
	
	for i in range(0, len(args)):
		arg = args[i]
		if len(arg)>0 and arg[0] == '{':
			# convert arg to dict()
			args[i] = json.loads(arg)
	print("args: {}".format(args))
	result = send_task(service_name, args=args)
	#print("result: {}".format(result.get(timeout=300)))
