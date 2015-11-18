# -*- coding: utf-8 -*-

import copy
from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from wapi.mall import models as mall_models
from wapi.mall import promotion_models
from utils import dateutil as utils_dateutil
import resource
from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
from cache import utils as cache_utils
from business.mall.order import Order
from business.mall.purchase_info import PurchaseInfo


class AOrder(api_resource.ApiResource):
	"""
	订单
	"""
	app = 'mall'
	resource = 'order'

	@param_required(['woid', 'ship_name', 'ship_address', 'ship_tel', 'order_type', 'xa-choseInterfaces'])
	def put(args):
		"""
		获取购物车项目

		@param id 商品ID
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		refueling_order = args.get('refueling_order', '')
		
		#解析购买参数
		purchase_info = PurchaseInfo.parse({
			'request_args': args
		})

		order = Order.create({
			"webapp_owner": webapp_owner,
			"webapp_user": webapp_user,
			"purchase_info": purchase_info,
		})

		# products = resource.get('mall', 'order_products', {
		# 	"woid": webapp_owner_id,
		# 	"webapp_owner_info": webapp_owner_info,
		# 	"webapp_user": webapp_user,
		# 	"member": member,
		# 	"product_info": product_info
		# })

		# pre_order = BPreOrder.get({
		# 	'woid': webapp_owner_id,
		# 	'webapp_owner_info': webapp_owner_info,
		# 	'webapp_user': webapp_user,
		# 	'member': member,
		# 	'products': products,
		# 	'request_args': args
		# })

		order_validation = order.validate()

		if (not order_validation['is_valid']):
			return 500, pre_order_validation['reason']

		if order.save():
			if order.final_price > 0 and purchase_info.used_pay_interface_type != '-1':
				# 处理 支付跳转路径
				# pay_interface = PayInterface.objects.get(owner_id=request.webapp_owner_id, type=pay_interface)
				pay_interface_data = filter(lambda x: x['type'] == int(purchase_info.used_pay_interface_type), webapp_owner.pay_interfaces)[0]
				pay_interface = mall_models.PayInterface.from_dict(pay_interface_data)
				#pay_url = pay_interface.pay(order, webapp_owner.id)
				pay_url = 'lala'

		data = {
			'order_id' : order.order_id,
			'id' : order.id,
			'final_price' : round(order.final_price, 2)
		}
		if pay_url:
			data['pay_url'] = pay_url

		return data