# -*- coding: utf-8 -*-
"""@package business.inegral_allocator.IntegralResourceAllocator
请求积分资源

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
from business.mall.realtime_stock import RealtimeStock


class ProductResource(business_model.Resource):
	"""商品资源
	"""
	__slots__ = (
		'type',
		'model_id',
		'purchase_count'
		)


	@staticmethod
	@param_required(['type'])
	def get(args):
		"""工厂方法，创建ProductResourcee对象

		@return ProductResource对象
		"""
		product_resource = ProductResource(args['type'])
		
		return product_resource

	def __init__(self, type):
		business_model.Resource.__init__(self)
		self.type = type
		self.model_id = 0
		self.purchase_count = 0

	def get_type(self):
		return self.type

	def get_resources(self, product):
		is_successed, reason = self.consume_stocks(product)
		if not is_successed:
			return False, reason

		#TODO 促销活动
		return True, reason

	def consume_stocks(self, product):
		"""
		消耗库存
		"""
		#请求分配库存资源
		realtime_stock = RealtimeStock.from_product_model_name({
				'model_name': product.model_name,
				'product_id': product.id
			})
		model2stock = realtime_stock.model2stock

		if not model2stock and len(model2stock) != 1:
			return False, u'商品已删除'

		current_model_id = model2stock.keys()[0]
		current_model = model2stock[current_model_id]

		if current_model['stock_type'] == mall_models.PRODUCT_STOCK_TYPE_LIMIT and product.purchase_count > current_model['stocks']:
			if current_model['stocks'] == 0:
				return False, 'sellout'
			else:
				return False, 'not_enough_stocks'
		else:
			mall_models.ProductModel.update(stocks=mall_models.ProductModel.stocks-product.purchase_count).dj_where(id=current_model_id).execute()			
			self.purchase_count = product.purchase_count
			self.model_id = current_model_id
			return True, product.purchase_count
