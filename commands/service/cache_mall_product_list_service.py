# -*- coding: utf-8 -*-
"""
缓存商品列表

@author bert
"""

import settings
import logging
from eaglet.core.exceptionutil import unicode_full_stack
from eaglet.core import watchdog
from eaglet.core.cache import utils as cache_utils

from commands.service_register import register
from api.mall.a_products import AProducts
from business.account.webapp_owner import WebAppOwner

@register("product_list")
def cache_product_list_service(data):
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
	category_id = data["category_id"]
	try:
		webapp_owner = WebAppOwner.get({
			'woid': woid
		})
		data['webapp_user'] = None
		data['webapp_owner'] = webapp_owner
		result = AProducts.get(data)
		cache_utils.set("w_%s_c_%s" % (woid, category_id), result)
	except:
		data['emg'] = unicode_full_stack()
		watchdog.error(data,server_name=settings.SERVICE_NAME)
	return
