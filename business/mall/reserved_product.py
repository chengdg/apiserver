# -*- coding: utf-8 -*-
"""@package business.mall.reserved_product
已预定商品

一个**已预定商品**指的是一个已经指定了相关**购买属性**的商品，这些**购买属性**包括：
1. 商品规格
2. 促销活动
3. 购买数量

在购物车、下单页面中，系统展示的商品都是**已预定商品**

已预订商品在生成订单时，需要预先扣除相关资源，这些资源来自购买属性，包括：
1. 库存
2. 积分
3. 促销活动

如果扣除资源失败，则会导致下单失败

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


class ReservedProduct(business_model.Model):
	"""已预订商品
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
		'shopping_cart_id', #兼容h5购物车页面的临时解决方案，后续需要将shopping_cart_id移出

		'shelve_type',
		'is_deleted',
		'stock_type',
		'stocks',
		'is_model_deleted',

		'can_use_coupon',
		'active_integral_sale_rule'
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'product_info'])
	def get(args):
		"""工厂方法，创建ShoppingCartProduct对象

		Parameters
			[in] product_info 商品信息
			{
				id: 商品id,
				model_name: 商品规格名,
				promotion_id: 商品促销id,
				shopping_cart_id: 购物车项的id,
				count: 商品数量
			}

		@return ReservedProduct对象
		"""
		reserved_product = ReservedProduct(args['webapp_owner'], args['webapp_user'], args['product_info'])

		return reserved_product

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

		self.can_use_coupon = True
		self.type = product.type
		self.id = product.id
		self.is_deleted = product.is_deleted
		self.shelve_type = product.shelve_type
		self.name = product.name
		self.thumbnails_url = product.thumbnails_url
		self.is_use_custom_model = product.is_use_custom_model
		self.shopping_cart_id = product_info.get('shopping_cart_id', 0)

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
		promotion_id = product_info.get('promotion_id', 0)
		if promotion_id == 0:
			#没有指定promotion，获取商品当前的promotion
			product_promotion = product.promotion
			if product_promotion and product_promotion.is_active() and product.promotion.can_use_for(webapp_user):
				self.promotion = product.promotion
			else:
				self.promotion = None
		else:
			#指定了promotion，获取指定的promotion
			self.promotion = {}

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


