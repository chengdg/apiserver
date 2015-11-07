# -*- coding: utf-8 -*-

#import sys
#import os

import settings
from resource.utils import resource_log
import datetime as dt
import time

from core import inner_resource as resource_module

class ApiNotExistError(Exception):
	pass

indent = 0

def resource_call(method, app, resource, data, req=None):
	resource_name = resource
	key = '%s-%s' % (app, resource)
	global indent

	start_at = time.clock()
	resource = resource_module.APPRESOURCE2CLASS.get(key, None)
	if not resource:
		resource_log(app, resource_name, method, data, (time.clock()-start_at), -1, indent)
		indent -= 1
		raise ApiNotExistError('%s:%s' % (key, method))

	func = getattr(resource['cls'], method, None)
	if not func:
		resource_log(app, resource_name, method, data, (time.clock()-start_at), -1, indent)
		indent -= 1
		raise ApiNotExistError('%s:%s' % (key, method))

	resource_log(app, resource_name, method, data, -999, 0, indent)
	indent += 1
	response = func(data)
	indent -= 1
	resource_log(app, resource_name, method, data, (time.clock()-start_at), 0, indent)
	return response


def get(app, resource, data):
	return resource_call('get', app, resource, data)


def post(app, resource, data):
	return resource_call('post', app, resource, data)


def put(app, resource, data):
	return resource_call('put', app, resource, data)


def delete(app, resource, data):
	return resource_call('delete', app, resource, data)
