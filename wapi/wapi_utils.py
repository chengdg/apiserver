#coding: utf8

from wapi.logger.mongo_logger import MongoAPILogger
import wapi
import settings
import logging
import json


_wapi_logger = None

def morph_params(param):
	"""
	将`webapp_user`和`webapp_owner`变成`wid`和`woid`

	@todo to be optimized
	"""
	new_param = {}
	for key, value in param.items():
		if key == 'webapp_user':
			new_param['wid'] = param['webapp_user'].id
		elif key == 'webapp_owner':
			new_param['woid'] = param['webapp_owner'].id
		else:
			new_param[key] = value
	return new_param


def param_to_text(param):
	"""
	将param转成JSON text，用于调试
	"""
	return json.dumps(morph_params(param))


def wapi_log(app, resource, method, params, time_in_s, status=0):
	"""
	记录WAPI信息，保存到mongo中
	"""
	if settings.WAPI_LOGGER_ENABLED:
		global _wapi_logger
		if _wapi_logger is None:
			_wapi_logger = MongoAPILogger()
		if settings.MODE == 'develop' or settings.MODE == 'test':
			logging.info("called WAPI (in {} s): {} {}/{}, param: {}".format(time_in_s, method, app, resource, param_to_text(params)))
		return _wapi_logger.log(app, resource, method, morph_params(params), time_in_s, status)
	else:
		logging.info("called WAPI (in {} s): {} {}/{}, param: {}".format(time_in_s, method, app, resource, param_to_text(params)))
	return
