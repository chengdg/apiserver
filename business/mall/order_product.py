# -*- coding: utf-8 -*-
"""@package business.mall.order_product
订单商品

一个订单商品是在商品业务对象的基础上，加上订单的相关信息，比如订单中商品的数量等，形成的新的业务对象。

与订单相关的业务流程，比如下单，获取订单详情等等，都不直接使用Product，而是使用OrderProduct

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


class OrderProduct(business_model.Model):
	"""订单商品
	"""
	__slots__ = (
		'id',
		'name',
		'type',
		'thumbnails_url',
		'pic_url',
		'member_discount',
		'purchase_count',
		'used_promotion_id',
		'total_price',
		'product_model_id',
		'_postage_config',
		'is_use_custom_model',

		'price',
		'original_price',
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
		'promotion',
		'shelve_type',
		'promotion_money'
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'product_info'])
	def get(args):
		"""工厂方法，创建OrderProduct对象

		@param[in] product_info 商品信息
			{
				id: 商品id,
				model_name: 商品规格名,
				promotion_id: 商品促销id,
				count: 商品数量
			}

		@return OrderProduct对象
		"""
		order_product = OrderProduct(args['webapp_owner'], args['webapp_user'], args['product_info'])

		return order_product

	def __init__(self, webapp_owner, webapp_user, product_info):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.__fill_detail(webapp_user, product_info)

		self.promotion_money = 0.0

	def __fill_detail(self, webapp_user, product_info):
		"""
		根据商品信息填充相应的商品详情
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
		self.type = product.type
		self.id = product.id
		self.name = product.name
		self.thumbnails_url = product.thumbnails_url
		self.pic_url = product.pic_url
		self.shelve_type = product.shelve_type
		self.is_use_custom_model = product.is_use_custom_model

		self.price = model.price
		self.original_price = model.price
		self.weight = model.weight
		self.stock_type = model.stock_type
		if not hasattr(product, 'min_limit'):
			self.min_limit = model.stocks
		self.stocks = model.stocks
		self.model_name = product_info['model_name']
		self.model = model
		self.is_model_deleted = False
		self.market_price = model.market_price
		self.product_model_id = '%s_%s' % (product_info['id'], product_info['model_name'])
		self.purchase_count = product_info['count']
		self.used_promotion_id = product_info['promotion_id']
		self.total_price = self.original_price * int(self.purchase_count)

		self.is_member_product = product.is_member_product

		#获取促销
		self.promotion = product.promotion

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

	def is_on_shelve(self):
		"""
		[property] 订单商品是否处于上架状态
		"""
		return self.context['product'].is_on_shelve()

	@cached_context_property
	def __current_model(self):
		"""
		[property] 实时的规格信息
		"""
		#TODO2: perf - 将这个操作放入OrderProducts进行批量处理
		product = self.context['product']
		for model in product.models:
			if self.model_name == model.name:
				model_id = model.id

		db_product_model = mall_models.ProductModel.get(id=model_id)

		return db_product_model.to_dict()

	def check_stocks(self):
		"""
		检查库存

		@return 
			is_sufficient: 库存是否充足
			reason: 如果is_sufficient为False, 这里是库存不足的原因; 如果is_sufficient为True, reason为None
		"""
		current_model = self.__current_model
		if current_model.get('is_deleted', True):
			return {
				"is_sufficient": False,
				"reason": "deleted"
			}

		if current_model['stock_type'] == mall_models.PRODUCT_STOCK_TYPE_LIMIT and self.purchase_count > current_model['stocks']:
			if current_model['stocks'] == 0:
				return {
					"is_sufficient": False,
					"reason": "sellout"
				}
			else:
				return {
					"is_sufficient": False,
					"reason": "not_enough_stocks"
				}
		else:
			return {
				"is_sufficient": True,
				"reason": None
			} 

	def consume_stocks(self):
		"""
		消耗库存
		"""
		#TODO2: 库存在self.check_stocks()时，就应该被扣除
		current_model = self.__current_model
		if current_model['stock_type'] == mall_models.PRODUCT_STOCK_TYPE_LIMIT:
			#counter=Stat.counter + 1
			mall_models.ProductModel.update(stocks=mall_models.ProductModel.stocks-self.purchase_count).dj_where(id=current_model['id']).execute()

	@cached_context_property
	def discount_money(self):
		"""
		[property] 订单商品的折扣金额
		"""
		# 目前product.member_discount_money 只有限时抢购会设置成0，不用乘商品数量
		return self.total_price * self.member_discount

	@property
	def supplier(self):
		"""
		[property] 订单商品的供应商
		"""
		return self.context['product'].owner_id

	def to_dict(self):
		data = business_model.Model.to_dict(self)
		data['postage_config'] = data['_postage_config']
		data['model'] = self.model.to_dict() if self.model else None
		data['promotion'] = self.promotion.to_dict() if self.promotion else None
		return data


