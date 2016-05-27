# -*- coding: utf-8 -*-
from eaglet.core import api_resource
from eaglet.decorator import param_required

import db.mall.models as mall_models
from business.mall.order import Order


class AAliPayInterface(api_resource.ApiResource):
	"""
	获取订单微信支付的参数信息
	"""
	app = 'pay'
	resource = 'alipay_interface'

	@param_required(['order_id'])
	def get(args):
		"""
		获取订单微信支付的参数信息

		@param order_id
		"""

		order = Order.from_id({
			'webapp_owner': args['webapp_owner'],
			'webapp_user': args['webapp_user'],
			'order_id': args['order_id']
		})

		pay_info = order.pay_info_for_pay_module(pay_interface_type=mall_models.PAY_INTERFACE_ALIPAY)
		return pay_info
