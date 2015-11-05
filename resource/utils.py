#coding: utf8

from wapi.logger.mongo_logger import MongoAPILogger
import settings


_resource_logger = None

def resource_log(app, resource, method, params, time_in_s, status=0):
	"""
	记录WAPI信息，保存到mongo中
	"""
	if settings.WAPI_LOGGER_ENABLED:
		global _resource_logger
		if _resource_logger is None:
			_resource_logger = MongoAPILogger()
		if settings.MODE == 'develop' or settings.MODE == 'test':
			print("called RESOURCE (in {} s): {} {}/{}, param: {}".format(time_in_s, method, app, resource, params))
		return _resource_logger.log(app, resource, method, params, time_in_s, status)
	return
