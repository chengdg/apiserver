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
		self.context['resource'] = None

	def release(self):
		if self.context['resource']:
			resource = self.context['resource']
			#TODo-bert 异常处理
			model_id = resource.model_id
			purchase_count = resource.purchase_count
			mall_models.ProductModel.update(stocks=mall_models.ProductModel.stocks+purchase_count).dj_where(id=model_id).execute()

	def allocate_resource(self, product):
	 	product_resource = ProductResource.get({
				'type': business_model.RESOURCE_TYPE_PRODUCT
			})

		successed, reason = product_resource.get_resources(product)
		if not successed:
			return False, reason, None
		else:
			self.context['resource'] = product_resource
			return True, reason, product_resource

		