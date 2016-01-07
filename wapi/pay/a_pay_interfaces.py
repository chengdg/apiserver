# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
# import resource
from business.mall.pay_interface import PayInterface


class APayResult(api_resource.ApiResource):
	"""
	显示支付方式列表
	"""
	app = 'pay'
	resource = 'pay_interfaces'

	@param_required(['order_id'])
	def get(args):
		"""
		显示支付方式列表

		@param order_id: order.id
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']

		order_id = args['order_id']

		pay_interfaces = PayInterface.get_order_pay_interfaces(webapp_owner, webapp_user, order_id)

		return {
			'order_id': order_id,
			'pay_interfaces': pay_interfaces
		}
