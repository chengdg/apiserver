# -*- coding: utf-8 -*-

import copy
from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from utils import dateutil as utils_dateutil
import resource
from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
from core.cache import utils as cache_utils
from business.mall.order_factory import OrderFactory
from business.mall.purchase_info import PurchaseInfo
from business.mall.pay_interface import PayInterface


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

		order_factory = OrderFactory.create({
			"webapp_owner": webapp_owner,
			"webapp_user": webapp_user,
			"purchase_info": purchase_info,
		})

		order_validation = order_factory.validate()

		if (not order_validation['is_valid']):
			return 500, pre_order_validation['reason']

		order = order_factory.save()
		if order:
			if order.final_price > 0 and purchase_info.used_pay_interface_type != '-1':
				pay_interface = PayInterface.from_type({
					"webapp_owner": webapp_owner,
					"pay_interface_type": purchase_info.used_pay_interface_type
				})
				pay_url = pay_interface.get_pay_url_for_order(order)

		data = {
			'order_id' : order.order_id,
			'id' : order.id,
			'final_price' : round(order.final_price, 2)
		}
		if pay_url:
			data['pay_url'] = pay_url

		return data


