# -*- coding: utf-8 -*-
"""@package business.mall.shopping_cart_product
购物车商品

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


class ShoppingCartProduct(business_model.Model):
	"""订单商品
	"""
	__slots__ = (
		'id',
		'name',
		'type',
		'thumbnails_url',
		'purchase_count',
		'product_model_id',
		'is_use_custom_model',
		'weight',

		'price',
		'original_price',
		'min_limit',
		'model_name',
		'member_discount',
		'model',
		'is_member_product',
		'promotion',
		'shopping_cart_id',
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'product_info'])
	def get(args):
		"""工厂方法，创建ShoppingCartProduct对象

		@return ShoppingCartProduct对象
		"""
		shopping_cart_product = ShoppingCartProduct(args['webapp_owner'], args['webapp_user'], args['product_info'])

		return shopping_cart_product

	def __init__(self, webapp_owner, webapp_user, product_info):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user
		self.__fill_detail(webapp_user, product_info)

		
	def __fill_detail(self, webapp_user, product_info):
		"""
		获得指定规格的商品详情
		"""
		product = Product.from_id({
			"webapp_owner": self.context['webapp_owner'],
			"member": webapp_user.member,
			"product_id": product_info['id']
		})
		self.context['product'] = product

		model = product.get_specific_model(product_info['model_name'])
		self.type = product.type
		self.id = product.id
		self.name = product.name
		self.thumbnails_url = product.thumbnails_url
		self.is_use_custom_model = product.is_use_custom_model
		self.shopping_cart_id = product_info['shopping_cart_id']

		self.price = float(model['price'])
		self.original_price = float(model['price'])
		self.weight = float(model['weight'])
		if not hasattr(product, 'min_limit'):
			self.min_limit = model['stocks']
		self.model_name = product_info['model_name']
		self.model = model
		self.product_model_id = '%s_%s' % (product_info['id'], product_info['model_name'])
		self.purchase_count = product_info['count']
		
		self.is_member_product = product.is_member_product
		self.promotion = product.promotion

		if product.is_member_product:
			_, self.member_discount = webapp_user.member.discount
		else:
			self.member_discount = 1.00
		self.price = self.price * self.member_discount #折扣后的价格
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

	def to_dict(self):
		data = business_model.Model.to_dict(self)
		data['postage_config'] = self.postage_config
		return data
