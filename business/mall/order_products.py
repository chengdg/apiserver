# -*- coding: utf-8 -*-

"""订单商品集合

"""

import json
from bs4 import BeautifulSoup
import math
import itertools

from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
import settings


class OrderProducts(business_model.Model):
	"""订单商品集合
	"""
	__slots__ = (
		'products',
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'purchase_info'])
	def get(args):
		"""工厂方法，创建OrderProducts对象

		@param[in] woid
		@param[in] webapp_user
		@param[in] webapp_owner_info
		@param[in] purchase_info: 购买信息PurchaseInfo对象

		@return OrderProducts对象
		"""
		order_products = OrderProducts()
		order_products.get_products(args['webapp_owner'], args['webapp_user'], args['purchase_info'])

		return order_products

	def __init__(self):
		business_model.Model.__init__(self)

	def get_products(self, webapp_owner, webapp_user, purchase_info):
		'''获取商品集合
		'''
		member = webapp_user.member

		product_ids = purchase_info['product_ids']
		promotion_ids = purchase_info['promotion_ids']
		product_counts = purchase_info['product_counts']
		product_model_names = purchase_info['product_model_names']
		self.products = []
		product_infos = []
		product2count = {}
		product2promotion = {}

		for i in range(len(product_ids)):
			product_id = int(product_ids[i])
			product_model_name = product_model_names[i]
			product_count = int(product_counts[i])
			product_promotion_id = promotion_ids[i] if promotion_ids[i] else 0
			product_info = {
				"id": product_id,
				"model_name": product_model_name,
				"count": count,
				"promotion_id": product_promotion_id
			}
			self.products.append(OrderProduct.get({
				"webapp_owner": webapp_owner,
				"webapp_user": webapp_user,
				"product_info": product_info
			}))
		