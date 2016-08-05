# -*- coding: utf-8 -*-
from eaglet.core import api_resource
from eaglet.decorator import param_required
from business.mall.order import Order
import db.mall.models as mall_models


class AKangouInterface(api_resource.ApiResource):
	"""
	获取订单微信支付的参数信息
	"""
	app = 'pay'
	resource = 'kangou_pay_interface'

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

		pay_info = order.pay_info_for_pay_module(pay_interface_type=mall_models.PAY_INTERFACE_KANGOU)
		return pay_info
