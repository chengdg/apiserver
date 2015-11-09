# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup
import math

#from core import resource
from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
import settings
import resource
from core import inner_resource
from core.watchdog.utils import watchdog_alert


class ROrder(inner_resource.Resource):
	"""
	商品详情
	"""
	app = 'mall'
	resource = 'order'

	def create_order(webapp_owner_id, webapp_user, product):
		"""
		mall_api:create_order
		创建一个order

		下订单页面调用
		"""
		order = mall_models.Order()
		if webapp_user.ship_info:
			ship_info = webapp_user.ship_info
			order.ship_name = ship_info.ship_name
			order.area = ship_info.area
			order.ship_address = ship_info.ship_address
			order.ship_tel = ship_info.ship_tel
			order.ship_id = ship_info.id

		# 积分订单
		if product.type == mall_models.PRODUCT_INTEGRAL_TYPE:
			order.type = mall_models.PRODUCT_INTEGRAL_TYPE

		#计算折扣
		product.original_price = product.price
		order.products = [product]

		order.postage = 0.0 #订单运费由前台计算

		return order

	@staticmethod
	def get_order_usable_integral(order, integral_info):
		"""
		mall_api:get_order_usable_integral
		获得订单中用户可以使用的积分
		"""
		user_integral = 0
		order_integral = 0
		total_money = sum([product.price*product.purchase_count for product in order.products])
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
		if hasattr(order, 'postage'):
			total_money = total_money + order.postage

		order_integral = math.ceil(total_money*usable_integral_percentage_in_order*count_per_yuan/100.0)

		if user_integral > order_integral:
			return int(order_integral)
		else:
			return int(user_integral)

	@param_required(['woid', 'webapp_user', 'member', 'products'])
	def get(args):
		webapp_owner_id = args['woid']
		webapp_user = args['webapp_user']
		webapp_owner_info = args['webapp_owner_info']
		member = args['member']
		products = args['products']

		product = products[0]
		order = ROrder.create_order(webapp_owner_id, webapp_user, product)

		#支付方式
		order.pay_interfaces = resource.get('mall', 'product_pay_interfaces', {
			'webapp_user': webapp_user,
			'products': products
		})

		#按促销进行product分组
		order.product_groups = resource.get('mall', 'product_groups', {
			'webapp_owner_info': webapp_owner_info,
			'member': member,
			'products': products
		})

		#获取订单可用积分
		integral_info = webapp_user.integral_info
		order.usable_integral = ROrder.get_order_usable_integral(order, integral_info)

		if 'return_model' in args:
			return order
		else:
			for product_group in order.product_groups:
				new_products = []
				for product in products:
					data = product.to_dict()
					data['order_thumbnails_url'] = product.order_thumbnails_url
					data['model_name'] = product.model_name
					data['purchase_count'] = product.purchase_count
					data['original_price'] = product.original_price
					new_products.append(data)
				product_group['products'] = new_products

			return order.to_dict(
				'products', 
				'postage', 
				'product_groups', 
				'usable_integral', 
				'pay_interfaces',
				'get_str_area'
			)
