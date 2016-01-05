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
#from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.mall.realtime_stock import RealtimeStock
from core.decorator import deprecated
from business.resource.product_resource_checker import ProductResourceChecker

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

	@deprecated
	def get_resources(self, product):
		"""
		@todo 需要将这段代码迁移到ProductResourceAllocator中
		"""

		product_resource_checker = ProductResourceChecker()

		is_succeeded, reason = product_resource_checker.check(product)

		if not is_succeeded:
			logging.info("reason in `ProductResource.get_resources(): {}".format(reason))
			return False, reason

		is_succeeded, reason = self.consume_stocks(product)
		if not is_succeeded:
			logging.info("reason in `ProductResource.get_resources(): {}".format(reason))
			return False, reason

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
			return False, {
				'is_successed': False,
				'type': 'product:is_deleted',
				'msg': u'商品已删除',
				'short_msg': u'商品已删除'
			}

		current_model_id = model2stock.keys()[0]
		current_model = model2stock[current_model_id]

		if current_model['stock_type'] == mall_models.PRODUCT_STOCK_TYPE_LIMIT and product.purchase_count > current_model['stocks']:
			if current_model['stocks'] == 0:
				return False, {
					'is_successed': False,
					'type': 'product:sellout',
					'msg': u'商品已售罄',
					'short_msg': u'商品已售罄'
				}
			else:
				return False, {
					'is_successed': False,
					'type': 'product:not_enough_stocks',
					'msg': u'',
					'short_msg': u'库存不足'
				}
		else:
			mall_models.ProductModel.update(stocks=mall_models.ProductModel.stocks-product.purchase_count).dj_where(id=current_model_id).execute()			
			self.purchase_count = product.purchase_count
			self.model_id = current_model_id
			return True, {
				'is_successed': True,
				'count': product.purchase_count
			}
