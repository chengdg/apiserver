# -*- coding: utf-8 -*-
"""@package business.mall.log_operator
操作日志记录器

"""

from db.mall import models as mall_models
from db.wzcard import models as wzcard_models
from business.mall import Supplier
import logging

class LogOperator(business_model.Model):
	"""操作日志记录器
	"""
	__slots__ = (
	)

	@staticmethod
	def record_operation_log(order, operator, action):
		"""
		创建订单操作日志
		"""
		logging.info("to create an OrderOperationLog...")
		if order.origin_order_id > 0 and order.supplier > 0:  #add by duhao 如果是子订单，则加入供应商信息
			action = '%s - %s' % (action, Supplier.get_supplier_name(order.supplier))

		order_operation_log = mall_models.OrderOperationLog.create(
			order_id = order.order_id,
			action = action,
			operator = operator
		)
		return order_operation_log


	@staticmethod
	def record_status_log(order, operator, from_status, to_status):
		"""
		创建订单状态日志
		"""
		logging.info("to create an OrderStatusLog...")
		order_status_log = mall_models.OrderStatusLog.create(
			order_id = order.order_id,
			from_status = from_status,
			to_status = to_status,
			operator = operator
		)
		return order_status_log


	@staticmethod
	def record_wzcard_log(webapp_owner, order_id, card_id, money, event_type=wzcard_models.WEIZOOM_CARD_LOG_TYPE_BUY_USE):
		"""
		记录微众卡日志
		"""
		logging.info("to create an WeizoomCardHasOrder log...")
		wzcard_log = wzcard_models.WeizoomCardHasOrder.create(
			owner_id = webapp_owner.id,
			order_id = order_id,
			card_id = card_id,
			money = money,
			event_type = event_type,
		)
		return wzcard_log