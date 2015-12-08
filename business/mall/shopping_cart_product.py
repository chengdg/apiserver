# -*- coding: utf-8 -*-
"""@package business.mall.shopping_cart_product
购物车商品

一个**购物车商品**是在商品业务对象的基础上，加上购物车的相关信息，比如购物车中商品的数量等，形成的新的业务对象。

与购物车相关的业务流程，比如获取购物车列表详情等等，都不直接使用Product，而是使用ShoppingCartProduct

"""

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


class ShoppingCartProduct(business_model.Model):
	"""购物车商品
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

		'shelve_type',
		'is_deleted',
		'stock_type',
		'stocks',
		'is_model_deleted'
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'product_info'])
	def get(args):
		"""工厂方法，创建ShoppingCartProduct对象

		@param[in] product_info 商品信息
			{
				id: 商品id,
				model_name: 商品规格名,
				shopping_cart_id: 购物车项的id,
				count: 商品数量
			}

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
		填充购物车商品的详情
		"""
		product = Product.from_id({
			"webapp_owner": self.context['webapp_owner'],
			"member": webapp_user.member,
			"product_id": product_info['id']
		})
		self.context['product'] = product

		self.type = product.type
		self.id = product.id
		self.is_deleted = product.is_deleted
		self.shelve_type = product.shelve_type
		self.name = product.name
		self.thumbnails_url = product.thumbnails_url
		self.is_use_custom_model = product.is_use_custom_model
		self.shopping_cart_id = product_info['shopping_cart_id']

		#获取商品规格信息
		model = product.get_specific_model(product_info['model_name'])
		self.is_model_deleted = model.is_deleted
		self.price = model.price
		self.original_price = model.price
		self.weight = model.weight
		if not hasattr(product, 'min_limit'):
			self.min_limit = model.stocks
		self.model_name = product_info['model_name']
		self.stock_type = model.stock_type
		self.stocks = model.stocks
		self.model = model

		self.product_model_id = '%s_%s' % (product_info['id'], product_info['model_name'])
		self.purchase_count = product_info['count']
		
		self.is_member_product = product.is_member_product

		#获取促销
		product_promotion = product.promotion
		if product_promotion and product_promotion.is_active() and product.promotion.can_use_for(webapp_user):
			self.promotion = product.promotion
		else:
			self.promotion = None

		if product.is_member_product:
			_, discount_value = webapp_user.member.discount
			self.member_discount = member_discount / 100.0
		else:
			self.member_discount = 1.00
		self.price = round(self.price * self.member_discount, 2) #折扣后的价格
		#TODO2: 为微众商城增加1.1的价格因子

	@cached_context_property
	def postage_config(self):
		"""
		[property] 购物车商品的运费策略
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
		data['model'] = self.model.to_dict() if self.model else None
		data['promotion'] = self.promotion.to_dict() if self.promotion else None
		return data


