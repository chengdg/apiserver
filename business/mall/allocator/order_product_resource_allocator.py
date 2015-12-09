# -*- coding: utf-8 -*-
"""@package business.mall.allocator.OrderProductResourceAllocator
请求商品库存资源

"""
import logging
import json
from bs4 import BeautifulSoup
import math
import itertools
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.resource.product_resource import ProductResource

class OrderProductResourceAllocator(business_model.Service):
	"""请求商品库存资源
	"""
	__slots__ = (
		'order',
		'result'
		)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		self.context['resources'] = []


	def release(self):
		#TODO-bert
		for resource in self.context['resources']:
			resource.release()

	def allocate_resource(self, order, purchase_info):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		products = order.products
		successed = False
		for product in products:
		 	product_resource = ProductResource.get({
					'type': business_model.RESOURCE_TYPE_PRODUCT,
					'webapp_user': webapp_user
				})

		 	successed,reason = product_resource.get_resources(product)
		 	if not successed:
		 		self.release()
		 		break
		 	else:
		 		self.context['resources'].append(product_resource)

		if not successed:
			return False, reason, self.context['resources']
		else:
		 	return True, reason, self.context['resources']

		