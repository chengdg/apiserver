# -*- coding: utf-8 -*-

import settings
import peewee
import json
import copy

import cache

class SqlMonitorMiddleware(object):
	def process_request(self, request, response):
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
			cache.utils.clear_db()
