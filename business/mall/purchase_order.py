# -*- coding: utf-8 -*-
"""@package business.mall.purchase_order
用于支持购买过程中进行订单编辑的订单

**购买订单**与**订单**在系统中是两个不同的业务对象，购买订单表示未下单之前的订单，而订单表示已成功下单后的订单。

两者的区别可以举一个例子：在购买订单中，支付方式是在下单时可以选用的所有支付方式的集合；而在订单中，支付方式是下单时选择的支付方式。

"""

import json
from bs4 import BeautifulSoup
import math
import itertools

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from eaglet.core import watchdog
from business import model as business_model
from business.mall.product import Product
import settings
from util import regional_util
from business.decorator import cached_context_property
from business.mall.reserved_product_repository import ReservedProductRepository
from business.mall.group_reserved_product_service import GroupReservedProductService


class PurchaseOrder(business_model.Model):
	"""用于支持购买过程中进行订单编辑的订单
	"""
	__slots__ = (
		'id',
		'type',
		'ship_info',
		'products',
		'postage',
		'promotion_product_groups',
		'pay_interfaces',
		'usable_integral',
		'is_enable_bill',
		'is_delivery'
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'purchase_info'])
	def create(args):
		"""工厂方法，创建PurchaseOrder业务对象

		@param[in] webapp_owner
		@param[in] webapp_user
		@param[in] purchase_info: PurchaseInfo业务对象

		@return PurchaseOrder对象
		"""
		order = PurchaseOrder(args['webapp_owner'], args['webapp_user'], args['purchase_info'])

		return order

	def __init__(self, webapp_owner, webapp_user, purchase_info):
		business_model.Model.__init__(self)

		self.type = mall_models.PRODUCT_DEFAULT_TYPE

		#计算折扣
		#product.original_price = product.price
		reserved_product_repository = ReservedProductRepository.get({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user
		})
		self.products = reserved_product_repository.get_reserved_products_from_purchase_info(purchase_info)
		# 积分订单
		temp_product = self.products[0]
		if temp_product.type == mall_models.PRODUCT_INTEGRAL_TYPE:
			self.type = mall_models.PRODUCT_INTEGRAL_TYPE

		#订单运费由前台计算
		self.postage = 0.0

		#按促销进行product分组
		group_reserved_product_service = GroupReservedProductService.get(webapp_owner, webapp_user)
		self.promotion_product_groups = group_reserved_product_service.group_product_by_promotion(self.products)

		if webapp_owner.user_profile.webapp_type:
			supplier_product_groups = {}
			for product in self.products:
				key = '%d-%d' % (product.supplier, product.supplier_user_id)
				if supplier_product_groups.has_key(key):
					supplier_product_groups[key].append(product)
				else:
					supplier_product_groups[key] = [product]
			for key, value in supplier_product_groups.items():
				supplier_product_groups[key] = group_reserved_product_service.group_product_by_promotion(value)
				for group in supplier_product_groups[key]:
					group.apply_promotion()
			self.promotion_product_groups = supplier_product_groups

		if not webapp_owner.user_profile.webapp_type:
			#对每一个group应用促销活动
			for promotion_product_group in self.promotion_product_groups:
				promotion_product_group.apply_promotion()

		#获取订单可用积分
		integral_info = webapp_user.integral_info
		self.usable_integral = self.__get_usable_integral(integral_info)

		#根据商品的支付方式配置，确定支付方式集合
		#只有所有商品都配置了"货到付款", 订单才会有"货到付款"的支付方式
		self.pay_interfaces = webapp_owner.pay_interfaces
		is_use_cod = True
		for product in self.products:
			if not product.is_use_cod_pay_interface:
				is_use_cod = False
				break
		self.is_enable_bill = False
		for product in self.products:
			if product.is_enable_bill:
				self.is_enable_bill = True

		if not is_use_cod:
			self.pay_interfaces = filter(lambda x: x['type'] != mall_models.PAY_INTERFACE_COD, self.pay_interfaces)
		#添加判断是否需要配送时间(是否勾选配送时间)
		self.is_delivery = False
		for product in self.products:
			if product.is_delivery == True:
				self.is_delivery = True
				break
		#添加判断是否需要配送时间
	def __get_usable_integral(self, integral_info):
		"""获得订单中用户可以使用的积分
		"""
		user_integral = 0
		order_integral = 0
		total_money = sum([product.price * product.purchase_count for product in self.products])
		user_integral = integral_info['count']
		usable_integral_percentage_in_order = integral_info['usable_integral_percentage_in_order']
		count_per_yuan = integral_info['count_per_yuan']
		if usable_integral_percentage_in_order:
			pass
		else:
			usable_integral_percentage_in_order = 0
		if count_per_yuan:
			pass
		else:
			count_per_yuan = 0

		# 加上运费的价格 by liupeiyu
		total_money = total_money + self.postage

		order_integral = math.ceil(total_money*usable_integral_percentage_in_order*count_per_yuan/100.0)

		if user_integral > order_integral:
			return int(order_integral)
		else:
			return int(user_integral)


