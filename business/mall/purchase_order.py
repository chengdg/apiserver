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

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from utils import regional_util
from business.decorator import cached_context_property
from business.mall.order_products import OrderProducts
from business.mall.product_grouper import ProductGrouper


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
		'usable_integral'
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

		if webapp_user.ship_info:
			ship_info = webapp_user.ship_info
			self.ship_info = {
				"name": ship_info['name'],
				"id": ship_info['id'],
				"tel": ship_info['tel'],
				"address": ship_info['address'],
				"area": ship_info['area'],
				"display_area": regional_util.get_str_value_by_string_ids(ship_info['area'])
			}
		else:# TODO 收货地址
			self.ship_info = {
				"name": 1,
				"id": 2,
				"tel": 3,
				"address": 4,
				"area": 5,
				"display_area": 6
			}

		#计算折扣
		#product.original_price = product.price
		order_products = OrderProducts.get({
			"webapp_owner": webapp_owner,
			"webapp_user": webapp_user,
			"purchase_info": purchase_info
		})
		self.products = order_products.products

		# 积分订单
		temp_product = self.products[0]
		if temp_product.type == mall_models.PRODUCT_INTEGRAL_TYPE:
			self.type = mall_models.PRODUCT_INTEGRAL_TYPE

		#订单运费由前台计算
		self.postage = 0.0

		#支付方式
		self.pay_interfaces = webapp_owner.pay_interfaces

		#按促销进行product分组
		product_grouper = ProductGrouper()
		self.promotion_product_groups = product_grouper.group_product_by_promotion(webapp_user.member, self.products)

		#获取订单可用积分
		integral_info = webapp_user.integral_info
		self.usable_integral = self.__get_usable_integral(integral_info)

		# if 'return_model' in args:
		# 	return order
		# else:
		# 	for product_group in order.product_groups:
		# 		new_products = []
		# 		for product in products:
		# 			data = product.to_dict()
		# 			data['order_thumbnails_url'] = product.order_thumbnails_url
		# 			data['model_name'] = product.model_name
		# 			data['purchase_count'] = product.purchase_count
		# 			data['original_price'] = product.original_price
		# 			new_products.append(data)
		# 		product_group['products'] = new_products

		# 	return order.to_dict(
		# 		'products', 
		# 		'postage', 
		# 		'product_groups', 
		# 		'usable_integral', 
		# 		'pay_interfaces',
		# 		'get_str_area'
		# 	)

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


