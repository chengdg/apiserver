# -*- coding: utf-8 -*-
"""@package business.mall.allocator.product_resource_allocator.ProductResourceAllocator
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

class ProductResourceAllocator(business_model.Service):
	"""请求商品库存资源
	"""
	__slots__ = (
		)

	def __init__(self):
		business_model.Service.__init__(self)
		self.context['resources'] = []

	@staticmethod
	def release(resources):
		if not resources:
			return 

		for resource in resources:
			#TODO-bert 异常处理
			if resource.get_type() == business_model.RESOURCE_TYPE_PRODUCT:
				resource.release()

	def allocate_resource(self, product):
	 	product_resource = ProductResource.get({
				'type': business_model.RESOURCE_TYPE_PRODUCT
			})

		successed, reason = product_resource.get_resources(product)

		if not successed:
			return False, reason, None
		else:
			return True, reason, product_resource

		