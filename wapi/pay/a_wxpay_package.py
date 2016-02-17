# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
from business.mall.order import Order


class AWXPayPackage(api_resource.ApiResource):
	"""
	获取订单微信支付的package参数信息
	"""
	app = 'pay'
	resource = 'wxpay_package'

	@param_required(['order_id'])
	def get(args):
		"""
		获取订单微信支付的package参数信息

		@param order_id
		"""

		order = Order.from_id({
			'webapp_owner': args['webapp_owner'],
			'webapp_user': args['webapp_user'],
			'order_id': args['order_id'].split('-')[0]
		})

		package_info = order.wx_package_for_pay_module()

		return package_info
