# -*- coding: utf-8 -*-
"""
cache_global_navbar

@author bert
"""
import json

import settings
import logging
from eaglet.core.exceptionutil import unicode_full_stack
from eaglet.core import watchdog
from eaglet.core.cache import utils as cache_utils

from commands.service_register import register
from api.mall.a_global_navbar import AGlobalNavbar
from business.account.webapp_owner import WebAppOwner
import redis
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_CACHES_DB)

@register("global_navbar")
def cache_global_navbar_service(data):
	"""
	创建用户的service

	args格式
	```
	{
	"function":"ding",
	"args":{
	"content":"wtf?",
	"uuid": "80035247"
	}
	}
	```

	@param args dict格式的参数
	"""
	woid = data["woid"]
	try:
		webapp_owner = WebAppOwner.get({
			'woid': woid
		})
		data['webapp_user'] = None
		data['webapp_owner'] = webapp_owner
		result = AGlobalNavbar.get(data)
		result = {
			"data": result,
			"code": 200	
			}

		r.set("w_%s_g" % woid, json.dumps(result))
	except:
		data['emg'] = unicode_full_stack()
		watchdog.error(data,server_name=settings.SERVICE_NAME)
	return
