# -*- coding: utf-8 -*-
"""@package apimall.a_order
订单API

"""

import copy
from datetime import datetime

from eaglet.core import api_resource
from core.exceptionutil import unicode_full_stack
import settings
from eaglet.utils.lock import wapi_lock
from eaglet.decorator import param_required
from util import dateutil as utils_dateutil
#import resource
from api.mall.a_purchasing import APurchasing as PurchasingApiResource
from eaglet.core.cache import utils as cache_utils
from business.mall.order_factory import OrderFactory, OrderResourcesException
from business.mall.purchase_info import PurchaseInfo
from business.mall.pay_interface import PayInterface
from business.mall.order import Order
from business.mall.order_has_refund import OrderHasRefund
from eaglet.core import watchdog
from business.spread.member_spread import MemberSpread
import logging


class ARefund(api_resource.ApiResource):
	"""
	订单
	"""
	app = 'mall'
	resource = 'refund'

	@param_required(['woid', 'order_id'])

	def put(args):
		"""
		openapi 取消订单操作(退款)

		@param id 商品ID
		"""
				"""
		更改订单状态
		"""
		order_id = args['order_id']

		try:
			order = Order.from_id({
				'webapp_user': args['webapp_user'],
				'webapp_owner': args['webapp_owner'],
				'order_id': order_id
			})

			order.refund()



			msg = u"apiserver中修改订单状态失败, order_id:{}, action:{}, cause:\n{}".format(args['order_id'], args['action'], reason)
			watchdog.info(msg)

			if not validate_result:
				return 500, {'msg': reason}

			if action == 'cancel':
				order.cancel()
			elif action == 'finish':
				order.finish()
		except:
			notify_message = u"apiserver中修改订单状态失败, order_id:{}, action:{}, cause:\n{}".format(args['order_id'], args['action'], unicode_full_stack())
			watchdog.alert(notify_message)
			return 500, ''
