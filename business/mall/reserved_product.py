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

#import json
#from bs4 import BeautifulSoup
#import math
#import itertools
#from datetime import datetime

from wapi.decorators import param_required
##from wapi import wapi_utils
#from core.cache import utils as cache_util
from db.mall import models as mall_models
#from db.mall import promotion_models
#import resource
#from core.watchdog.utils import watchdog_alert
from business import model as business_model
from business.mall.product import Product
#import settings
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
		'is_use_cod_pay_interface',

		'price',
		'original_price',
		'total_price',
		'min_limit',
		'model_name',
		'member_discount',
		'model',
		'is_member_product',
		'promotion',
		'expected_promotion_id', #已预订商品期望促销
		'used_promotion_id', #已预订商品当前促销
		'promotion_result',
		'promotion_saved_money', #促销抵扣金额
		'shopping_cart_id', #兼容h5购物车页面的临时解决方案，后续需要将shopping_cart_id移出

		'shelve_type',
		'is_deleted',
		'stock_type',
		'stocks',
		'is_model_deleted',
		'postage_type',
		'unified_postage_money',

		'can_use_coupon',
		'integral_sale',
		'active_integral_sale_rule',
		'is_enable_bill',
		'is_delivery', # 是否勾选配送时间,
		'purchase_price'
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

	def __init__(self, webapp_owner, webapp_user, product_info=None):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user
		if product_info:
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
		self.integral_sale = product.integral_sale
		self.is_use_cod_pay_interface = product.is_use_cod_pay_interface
		self.min_limit = product.min_limit
		self.is_enable_bill = product.is_enable_bill
		self.purchase_price = product.purchase_price

		self.model_name = product_info['model_name']
		self.expected_promotion_id = product_info.get('expected_promotion_id', 0)
		self.product_model_id = '%s_%s' % (product_info['id'], product_info['model_name'])
		self.purchase_count = product_info['count']
		self.is_member_product = product.is_member_product

		self.postage_type = product.postage_type
		self.unified_postage_money = product.unified_postage_money
		self.is_delivery = product.is_delivery
		#获取商品规格信息
		model = product.get_specific_model(product_info['model_name'])
		if model:
			self.is_model_deleted = model.is_deleted
			self.price = model.price
			self.original_price = model.price
			self.weight = model.weight
			self.stock_type = model.stock_type
			self.stocks = model.stocks
			self.model = model
			self.total_price = self.original_price * int(self.purchase_count)
		else:
			self.is_model_deleted = True
			self.price = 0
			self.original_price = 0
			self.weight = 0
			self.stock_type = 0
			self.stocks =0
			self.model = ''
			self.total_price = 0

		#获取商品当前的promotion
		product_promotion = product.promotion
		if product_promotion and product_promotion.is_active() and product.promotion.can_use_for(webapp_user):
			self.promotion = product.promotion
			self.used_promotion_id = self.promotion.id
		else:
			self.promotion = None
			self.used_promotion_id = 0
		self.promotion_saved_money = 0.0

		#获取促销
		# promotion_id = product_info.get('promotion_id', 0)
		# if promotion_id == 0:
		# 	#没有指定promotion，获取商品当前的promotion
		# 	product_promotion = product.promotion
		# 	if product_promotion and product_promotion.is_active() and product.promotion.can_use_for(webapp_user):
		# 		self.promotion = product.promotion
		# 		self.used_promotion_id = self.promotion.id
		# 	else:
		# 		self.promotion = None
		# 		self.used_promotion_id = 0
		# else:
		# 	#指定了promotion，获取指定的promotion
		# 	self.promotion = {}
		# 	self.used_promotion_id = 0

		if product.is_member_product:
			_, discount_value = webapp_user.member.discount
			self.member_discount = discount_value / 100.0
		else:
			self.member_discount = 1.00
		self.price = round(self.price * self.member_discount, 2) #折扣后的价格

		self.context['is_disable_discount'] = False

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

	def disable_integral_sale(self):
		"""
		禁用积分应用
		"""
		self.integral_sale = None
		self.active_integral_sale_rule = None

	# def apply_promotion(self):
	# 	"""
	# 	对商品应用促销规则
	# 	"""
	# 	if self.promotion:
	# 		self.promotion.apply_promotion([self])

	def disable_promotion(self):
		"""
		禁用商品的促销规则
		"""
		self.used_promotion_id = 0
		self.promotion = None
		self.promotion_saved_money = 0.0
		self.promotion_result = None

	def set_promotion_result(self, promotion_result):
		"""
		设置商品的促销结果

		Parameters
			[in] promotion_result: 促销结果
		"""
		self.promotion_result = promotion_result
		self.promotion_saved_money = promotion_result.saved_money

		if self.promotion.type_name == 'flash_sale':
			#限时抢购，修改已预订商品购买价
			self.price = self.promotion.promotion_price

	def use_product_coupon(self, coupon):
		"""
		使用针对商品的优惠券(单品券)

		Parameters
			[in] coupon: 单品券的Coupon对象
		"""
		self.disable_discount()
		#在原价基础上应用单品券
		self.price = self.price - coupon.money

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

	def consume_stocks(self):
		"""
		消耗库存
		"""
		#TODO2: 将扣除库存的逻辑放入到ProductResourceAllocator中
		current_model = self.__current_model
		if current_model['stock_type'] == mall_models.PRODUCT_STOCK_TYPE_LIMIT:
			#counter=Stat.counter + 1
			mall_models.ProductModel.update(stocks=mall_models.ProductModel.stocks-self.purchase_count).dj_where(id=current_model['id']).execute()

	@cached_context_property
	def discount_money(self):
		"""
		[property] 订单商品的折扣金额
		"""
		if self.context['is_disable_discount']:
			return 0
		else:
			if self.promotion and self.promotion.type_name == 'flash_sale':
				return 0
			else:
				return self.total_price * (1 - self.member_discount)

	@property
	def supplier(self):
		"""
		[property] 订单商品的供应商
		"""
		return self.context['product'].supplier

	@property
	def supplier_user_id(self):
		"""
		[property] 订单商品的同步供应商id
		"""
		return self.context['product'].supplier_user_id

	@property
	def supplier_name(self):
		"""
		[property] 订单商品的同步供应商名称
		"""
		return self.context['product'].supplier_name

	def has_expected_promotion(self):
		"""
		判断已预订商品是否拥有预期的促销

		Returns
			如果拥有预期促销，返回True；否则，返回False
		"""
		return self.expected_promotion_id != 0

	def is_expected_promotion_active(self):
		"""
		判断预期促销是否还在进行中

		Returns
			如果预期促销还在进行中，返回True；否则，返回False
		"""
		return self.expected_promotion_id == self.used_promotion_id

	def disable_discount(self):
		"""
		禁用会员折扣
		"""
		self.context['is_disable_discount'] = True
		self.price = self.original_price

	def to_dict(self):
		data = business_model.Model.to_dict(self)
		data['postage_config'] = self.postage_config
		data['promotion_result'] = self.promotion_result.to_dict() if self.promotion_result else None
		data['model'] = self.model.to_dict() if self.model else None
		data['promotion'] = self.promotion.to_dict() if self.promotion else None
		data['integral_sale'] = self.integral_sale.to_dict() if self.integral_sale else None
		data['supplier_user_id'] = self.supplier_user_id
		data['supplier'] = self.supplier
		data['supplier_name'] = self.supplier_name
		return data


