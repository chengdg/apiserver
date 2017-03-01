# -*- coding: utf-8 -*-
import redis
import settings

from ..exceptionutil import unicode_full_stack
from eaglet.utils.stack_util import get_trace_back

from eaglet.core.zipkin import zipkin_client

if settings.REDIS_HOST:
	r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_CACHES_DB)
else:
	r = None

	
def hgetall(key):
	return r.hgetall(key)


def hmget(key_name, keys):
	return r.hmget(key_name, keys)


def hset(hash_name, key, value):
	r.hset(hash_name, key, value)


def get_cache(key_name):
	return r.get(key_name)

	
def get_no_trans_pipeline():
	return r.pipeline(False)


def get_trans_pipeline():
	return r.pipeline()

r.exists()


