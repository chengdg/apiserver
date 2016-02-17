# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
from business.mall.order import Order


class APayResult(api_resource.ApiResource):
	"""
	订单
	"""
	app = 'pay'
	resource = 'wxpay_interface'

	@param_required(['order_id'])
	def get(args):
		"""
		获取支付结果

		@param id 商品ID
		"""

		order = Order.from_id({
			'webapp_owner': args['webapp_owner'],
			'webapp_user': args['webapp_user'],
			'order_id': args['order_id']
		})

		return order.pay_info_for_pay_module


