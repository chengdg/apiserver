# -*- coding: utf-8 -*-

import settings
import peewee
import json
import copy
from datetime import datetime
import time

from eaglet.core import cache

from business.account.access_token import AccessToken 

import logging

class SqlMonitorMiddleware(object):
	def process_request(self, request, response):
		#import resource
		#resource.indent = 0
		
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
			access_token_keys = cache.utils.get_keys('access_token*')
			access_token_dict = {}

			for access_token_key in access_token_keys:
				access_token_dict[access_token_key] = cache.utils.GET_CACHE(access_token_key)
			
			cache.utils.clear_db()

			# 清理库4
			import redis
			r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_COMMON_DB)
			r.flushdb()

			for key,value in access_token_dict.items():
				cache.utils.SET_CACHE(key, value)


