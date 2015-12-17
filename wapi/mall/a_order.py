# -*- coding: utf-8 -*-
"""@package wapi.mall.a_order
订单API

"""

import copy
from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from utils import dateutil as utils_dateutil
#import resource
from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
from core.cache import utils as cache_utils
from business.mall.order_factory import OrderFactory, OrderException
from business.mall.purchase_info import PurchaseInfo
from business.mall.pay_interface import PayInterface
from business.mall.order import Order


class AOrder(api_resource.ApiResource):
	"""
	订单
	"""
	app = 'mall'
	resource = 'order'

	@param_required(['ship_name', 'ship_address', 'ship_tel', 'order_type', 'xa-choseInterfaces'])
	def put(args):
		"""
		下单接口

		@param id 商品ID
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		refueling_order = args.get('refueling_order', '')
		
		#解析购买参数
		purchase_info = PurchaseInfo.parse({
			'request_args': args
		})

		try:
			order_factory = OrderFactory.get({
				"webapp_owner": webapp_owner,
				"webapp_user": webapp_user
			})
			order = order_factory.create_order(purchase_info)
		except OrderException as e:
			return 500, {'detail': e.value}

		# order_factory = OrderFactory.get({
		# 	"webapp_owner": webapp_owner,
		# 	"webapp_user": webapp_user,
		# 	#"purchase_info": purchase_info,
		# })

		# order_validation = order_factory.validate()

		# if (not order_validation['is_valid']):
		# 	return 500, order_validation['reason']

		# order_validation = order_factory.resource_allocator()
		# if (not order_validation['is_valid']):
		# 	return 500, order_validation['reason']
		# else:
		# 	order = order_validation['order']

		# order = order_factory.save()
		pay_url_info = None
		if order:
			if purchase_info.used_pay_interface_type != '-1':
				pay_interface = PayInterface.from_type({
					"webapp_owner": webapp_owner,
					"pay_interface_type": purchase_info.used_pay_interface_type
				})
				pay_url_info = pay_interface.get_pay_url_info_for_order(order)

		data = {
			'order_id' : order.order_id,
			'id' : order.id,
			'final_price' : round(order.final_price, 2)
		}
		if pay_url_info:
			data['pay_url_info'] = pay_url_info

		return data

	@staticmethod
	def to_dict(order):
		order_dict = order.to_dict('latest_express_detail', 'products')
		api_keys = [
			"buyer_name",
			"coupon_money",
			"integral",
			"ship_area",
			"member_grade_id",
			"edit_money",
			"id",
			"pay_interface_name",
			"ship_name",
			"has_sub_order",
			"sub_orders",
			"product_price",
			"member_grade_discount",
			"supplier",
			"latest_express_detail",
			"type",
			"integral_each_yuan",
			"final_price",
			"status",
			"postage",
			"ship_address",
			"pay_interface_type",
			"order_id",
			"integral_money",
			"ship_tel",
			"origin_order_id",
			"coupon_id",
			"customer_message",
			"webapp_id",
			"promotion_saved_money",
			"express_number",
			"webapp_user_id",
			"products",
			"status_text",
			"created_at",
			"weizoom_card_money",
		]
		data = {}
		for key in api_keys:
			data[key] = order_dict.get(key)
		return {
			"order": data
		}

	@param_required(['order_id'])
	def get(args):
		order = Order.from_id({
			'webapp_owner': args['webapp_owner'],
			'webapp_user': args['webapp_user'],
			'order_id': args['order_id']
		})

		return AOrder.to_dict(order)