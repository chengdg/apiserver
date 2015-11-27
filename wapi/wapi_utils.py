#coding: utf8

from wapi.logger.mongo_logger import MongoAPILogger
import settings
import logging


_wapi_logger = None

def wapi_log(app, resource, method, params, time_in_s, status=0):
	"""
	记录WAPI信息，保存到mongo中
	"""
	if settings.WAPI_LOGGER_ENABLED:
		global _wapi_logger
		if _wapi_logger is None:
			_wapi_logger = MongoAPILogger()
		if settings.MODE == 'develop' or settings.MODE == 'test':
			logging.debug("called WAPI (in {} s): {} {}/{}, param: {}".format(time_in_s, method, app, resource, params))
		return _wapi_logger.log(app, resource, method, params, time_in_s, status)
	return


def get_webapp_id_via_oid(owner_id):
	"""

	@TODO to be implemented
	"""
	return 0
