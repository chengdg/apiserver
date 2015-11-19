# -*- coding: utf-8 -*-

__author__ = 'robert'

import datetime
import array

from utils.command import BaseCommand

from cache import utils as cache_util
from bson import json_util
import json

class Command(BaseCommand):
	help = "json.dumps cached value"
	args = ''
	
	def handle(self, key, **options):
		print key
		value = cache_util.get_cache(key)

		if value:
			value = self.__for_json_dumps(value)
			print json.dumps(value, default=json_util.default, indent=True)
		else:
			print 'no value'
		
	def __for_json_dumps(self, value):
		if isinstance(value, dict):
			del_keys = []
			for (k, v) in value.items():
				if isinstance(v, dict):
					v = self.__for_json_dumps(v)
				if isinstance(v, datetime.datetime):
					del_keys.append(k)
				if isinstance(v, datetime.date):
					del_keys.append(k)
				if k == 'product_review':
					del_keys.append(k)
			for key in del_keys:
				value[key] = []
			return value

