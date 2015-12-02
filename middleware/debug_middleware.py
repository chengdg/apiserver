# -*- coding: utf-8 -*-

import settings
import peewee
import json
import copy
from datetime import datetime
import time

from core import cache

from wapi.user.access_token import AccessToken

import logging

class SqlMonitorMiddleware(object):
	def process_request(self, request, response):
		import resource
		resource.indent = 0
		
		print 'empty peewee.QUERIES'
		peewee.QUERIES = []
		cache.utils.CACHE_QUERIES = []

	def process_response(self, request, response, resource):
		if settings.DEBUG and 'wapi' in request.path:
			if response.body:				
				obj = json.loads(response.body)
				obj['queries'] = copy.copy(peewee.QUERIES)
				obj['queries'].extend(copy.copy(cache.utils.CACHE_QUERIES))
				response.body = json.dumps(obj)


class RedisMiddleware(object):
	def process_request(self, request, response):
		if request.params.get('__nocache', None):
			access_token = request.params.get('access_token',None)
			value = None
			if access_token:
				account_info = AccessToken.get_sys_account({
					'access_token':access_token
				})
				if account_info:
					access_token = account_info.access_token
					date_str = datetime.today().strftime('%Y-%m-%d') 
					value = {
						'woid': account_info.woid,
						'openid': account_info.openid,
						'date_str': date_str,
						'expires_in': '100000000000',
						'times': int(time.time())
					}

			cache.utils.clear_db()

			if access_token and value:
				logging("keys:%s. value:%s" % (access_token, value))
				cache.utils.SET_CACHE(access_token, value)

