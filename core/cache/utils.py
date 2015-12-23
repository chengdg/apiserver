# -*- coding: utf-8 -*-

__author__ = 'bert'

import os
from time import time
import traceback
import logging
# Import the fastest implementation of
# pickle package. This should be removed
# when python3 come the unique supported
# python version
try:
    import cPickle as pickle
except ImportError:
    import pickle

import redis
import settings

from core.exceptionutil import unicode_full_stack

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_CACHES_DB)

CACHE_QUERIES = []

class Object(object):
	def __init__(self, name=""):
		self.name = name

	def to_dict(self):
		return self.__dict__

def modify_keys(function):
	def _modify_keys(*args, **kwargs):
		args = list(args)
		keys = args[0]
		if isinstance(keys, list):
			acture_keys = []
			for key in keys:
				acture_keys.append(':1:'+key)
			keys = acture_keys
		else:
			keys = ':1:' + keys
		args[0] = keys
		args = tuple(args)
		return function(*args, **kwargs)
	return _modify_keys

def get_trace_back():
	stack_entries = traceback.extract_stack()
	stack_entries = filter(lambda entry: (('apiserver' in entry[0]) and (not 'cache%sutils' % os.path.sep in entry[0])), stack_entries)
	buf = []
	for stack_entry in stack_entries:
		filename, line, function_name, text = stack_entry
		formated_stack_entry = "<span>File `%s`, line %s, in %s</span><br/><span>&nbsp;&nbsp;&nbsp;&nbsp;%s</span>" % (filename, line, function_name, text)
		buf.append(formated_stack_entry)
	stack = '<br/>'.join(buf).replace("\\", '/').replace('"', "``").replace("'", '`')
	return stack

@modify_keys
def set_cache(key, value, timeout=0):
	pickled_value = pickle.dumps(value)
	r.set(key, pickled_value)

@modify_keys
def get_cache(key):
	value = r.get(key)
	if not value:
		return value
	return pickle.loads(value)
	# return r.get(key)

@modify_keys
def get_many(keys):
	return [pickle.loads(value) if value else value for value in r.mget(keys)]

@modify_keys
def delete_cache(key):
	r.delete(key)
	#r.delete(':1:'+key)

@modify_keys
def delete_pattern(key):
	keys = r.keys(key)

def clear_db():
	r.flushdb()

def set_cache_wrapper(key, value, timeout=0):
	start = time()
	try:	
		return set_cache(key, value, timeout)
	except:
		if settings.DEBUG:
			raise
		else:
			return None
	finally:
		stop = time()
		duration = stop - start
		value_type = str(type(value)).replace('<', '&lt;').replace('>', '&gt;')
		CACHE_QUERIES.append({
			'sql': 'set `cache`: {`%s`: `%s`)' % (key, value_type),
			'time': "%.3f" % duration,
			'stack': get_trace_back()
		})
		
@modify_keys
def get_keys(pattern):
	keys = r.keys(pattern)
	return keys

def get_cache_wrapper(key):
	start = time()
	success = False
	try:
		value = get_cache(key)
		if value:
			success = True
		return value
	except:
		if settings.DEBUG:
			raise
		else:
			return None
	finally:
		stop = time()
		duration = stop - start
		CACHE_QUERIES.append({
			'sql': 'get `cache`: `%s` =&gt; %s' % (key, 'hit' if success else 'MISS!!'),
			'time': "%.3f" % duration,
			'stack': get_trace_back()
		})


def get_many_wrapper(keys):
	start = time()
	success = False
	try:
		value = get_many(keys)
		if value:
			success = True
		return value
	except:
		if settings.DEBUG:
			raise
		else:
			return None
	finally:
		stop = time()
		duration = stop - start
		CACHE_QUERIES.append({
			'sql': 'get_many from `cache`: `%s` =&gt; %s' % (keys, 'hit' if success else 'MISS!!'),
			'time': "%.3f" % duration,
			'stack': get_trace_back()
		})


def delete_cache_wrapper():
	start = time()
	try:
		return delete_cache()
	except:
		if settings.DEBUG:
			raise
		else:
			return None
	finally:
		value = 'delete_cache_wrapper'
		stop = time()
		duration = stop - start
		value_type = str(type(value)).replace('<', '&lt;').replace('>', '&gt;')
		CACHE_QUERIES.append({
			'sql': 'delete `cache`: {`%s`: `%s`)' % (key, value_type),
			'time': "%.3f" % duration,
			'stack': get_trace_back()
		})


def delete_pattern_wrapper(pattern):
	start = time()
	try:
		return delete_pattern(pattern)
	except:
		if settings.DEBUG:
			raise
		else:
			return None
	finally:
		value = 'delete_pattern_wrapper'
		stop = time()
		duration = stop - start
		value_type = str(type(value)).replace('<', '&lt;').replace('>', '&gt;')
		CACHE_QUERIES.append({
			'sql': 'delete_pattern from `cache`: `%s`' % pattern,
			'time': "%.3f" % duration,
			'stack': get_trace_back()
		})


if settings.MODE == 'develop':
	SET_CACHE = set_cache_wrapper
	GET_CACHE = get_cache_wrapper
	DELETE_CACHE = delete_cache_wrapper
	DELETE_PATTERN = delete_pattern_wrapper
	GET_MANY = get_many_wrapper
else:
	SET_CACHE = set_cache
	GET_CACHE = get_cache
	DELETE_CACHE = delete_cache
	DELETE_PATTERN = delete_pattern
	GET_MANY = get_many


def get_from_cache(key, on_miss):
	"""
	从cache获取数据，构建对象
	"""
	obj = GET_CACHE(key)
	if obj:
		return obj
	else:
		try:
			fresh_obj = on_miss()
			if not fresh_obj:
				return None
			value = fresh_obj['value']
			SET_CACHE(key, value)
			if 'keys' in fresh_obj:
				for fresh_key in fresh_obj['keys']:
					SET_CACHE(fresh_key, value)
			return value
		except:
			if settings.DEBUG:
				raise
			else:
				print unicode_full_stack()
				return None


def get_many_from_cache(key_infos):
	keys = []
	key2onmiss = {}

	for key_info in key_infos:
		key = key_info['key']
		keys.append(key)
		key2onmiss[key] = key_info['on_miss']

	values = GET_MANY(keys)
	objs = {}
	for i in range(len(keys)):
		key = keys[i]
		value = values[i]
		if value:
			objs[key] = value

	for key in keys:
		if objs.get(key, None):
			continue

		on_miss = key2onmiss[key]
		if on_miss:
			fresh_obj = on_miss()
			if not fresh_obj:
				value = {}
			else:
				value = fresh_obj['value']
				SET_CACHE(key, value)
			objs[key] = value

	return objs



