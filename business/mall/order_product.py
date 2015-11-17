# -*- coding: utf-8 -*-

"""订单商品

"""

import json
from bs4 import BeautifulSoup
import math
import itertools
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property


class OrderProduct(business_model.Model):
	"""订单商品
	"""
	__slots__ = (
		'id',
		'type',
		'member_discount',
		'purchase_count',
		'used_promotion_id',
		'total_price',
		'product_model_id',
		'_postage_config',

		'price',
		'_original_price',
		'weight',
		'stock_type',
		'stocks',
		'min_limit',
		'model_name',
		'model',
		'is_model_deleted',
		'market_price',
		'custom_model_properties',
		'total_price',
		'can_use_coupon',
		'is_member_product',
		'promotion'
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'product_info'])
	def get(args):
		"""工厂方法，创建OrderProduct对象

		@return OrderProduct对象
		"""
		order_product = OrderProduct(args['webapp_owner'], args['webapp_user'], args['product_info'])

		return order_product

	def __init__(self, webapp_owner, webapp_user, product_info):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.__fill_detail(webapp_user, product_info)

	def __fill_detail(self, webapp_user, product_info):
		"""
		mall_api:get_product_details_with_model
		获得指定规格的商品详情
		"""
		product = Product.from_id({
			"webapp_owner": self.context['webapp_owner'],
			"member": webapp_user.member,
			"product_id": product_info['id']
		})
		self.context['product'] = product

		#默认可以使用优惠券
		#TODO2：目前对商品是否可使用优惠券的设置放在了order_products中，主要是出于目前批量处理的考虑，后续应该将r_forbidden_coupon_product_ids资源进行优化，将判断逻辑放入到order_product中
		self.can_use_coupon = True

		model = product.get_specific_model(product_info['model_name'])
		self.type = product.type,
		self.id = product.id,
		self.price = model['price']
		self.weight = model['weight']
		self.stock_type = model['stock_type']
		if not hasattr(product, 'min_limit'):
			self.min_limit = model['stocks']
		self.stocks = model['stocks']
		self.model_name = product_info['model_name']
		self.model = model
		self.is_model_deleted = False
		self.market_price = model.get('market_price', 0.0)
		self.product_model_id = '%s_%s' % (product_info['id'], product_info['model_name'])
		self.purchase_count = product_info['count']
		self.used_promotion_id = product_info['promotion_id']
		self.total_price = float(self.price) * int(self.purchase_count)

		self.is_member_product = product.is_member_product
		print '-$-' * 30
		print product
		print type(product)
		print dir(product)
		print '-$-' * 30
		self.promotion = product.promotion

		if product.is_member_product:
			self.member_discount = webapp_user.member.discount
		else:
			self.member_discount = 1.00
		#TODO2: 为微众商城增加1.1的价格因子

	@cached_context_property
	def postage_config(self):
		"""
		[property] 订单商品的运费策略
		"""
		product = self.context['product']
		webapp_owner = self.context['webapp_owner']

		if product.postage_type == mall_models.POSTAGE_TYPE_UNIFIED:
			#使用统一运费
			return {
				"id": -1,
				"money": product.unified_postage_money,
				"factor": None
			}
		else:
			return webapp_owner.system_postage_config

	@property
	def original_price(self):
		"""
		[property] 订单商品的原始价格
		"""
		return self._original_price

	@original_price.setter
	def original_price(self, value):
		"""
		[property setter] 订单商品的原始价格
		"""
		self._original_price = value