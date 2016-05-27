# -*- coding: utf-8 -*-

import db.mall.models as mall_models
from business.mall.order import Order
from eaglet.core import api_resource
from core.exceptionutil import unicode_full_stack
from eaglet.core import watchdog
from eaglet.decorator import param_required


class APayResultH5(api_resource.ApiResource):
	"""
	订单
	"""
	app = 'pay'
	resource = 'pay_result_h5'


	@param_required(['order_id', 'pay_interface_type'])
	def put(args):
		"""
		@warning: 对外网开放的支付接口，只接受从h5支付方式列表发起的货到付款,高风险，改动需慎重
		"""

		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']

		order_id = args['order_id'].split('-')[0]
		pay_interface_type = int(args['pay_interface_type'])

		# 此接口只可使用货到付款

		if pay_interface_type !=mall_models.PAY_INTERFACE_COD:
			watchdog.alert('货到付款接口被异常调用,woid:%s,webapp_user_id:%s', (webapp_owner.id,webapp_user.id))
			return 500, {}
		order = Order.from_id({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user,
			'order_id': order_id
		})
		try:
			is_success, msg = order.pay(pay_interface_type=mall_models.PAY_INTERFACE_COD)
		except:
			is_success = False
			msg = unicode_full_stack()
			watchdog.alert(msg)
		return {
			'order_id': args['order_id'],
			'is_success': is_success,
		}

