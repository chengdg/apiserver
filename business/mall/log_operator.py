# -*- coding: utf-8 -*-
"""@package business.mall.log_operator
操作日志记录器

@todo 待重构（这个应该包括在WZCard中）
"""
from business import model as business_model
from db.mall import models as mall_models
from db.wzcard import models as wzcard_models
from business.mall.supplier import Supplier
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

		# 记录子订单日志
		if order.origin_order_id == -1:
			for order_id in order.get_sub_order_ids():
				order_operation_log = mall_models.OrderOperationLog.create(
					order_id=order_id,
					action=action,
					operator=operator
				)

		return order_operation_log


	# @staticmethod
	# def record_wzcard_log(owner_id, order_id, card_id, money, event_type=wzcard_models.WEIZOOM_CARD_LOG_TYPE_BUY_USE):
	# 	"""
	# 	记录微众卡日志
	# 	"""
	# 	logging.info("to create an WeizoomCardHasOrder log: order_id={}, card_id={}, money={}, event_type={}".format(order_id, card_id, money, event_type))
	# 	wzcard_log = wzcard_models.WeizoomCardHasOrder.create(
	# 		owner_id = owner_id,
	# 		order_id = order_id,
	# 		card_id = card_id,
	# 		money = money,
	# 		event_type = event_type,
	# 	)
	# 	return wzcard_log

	# @staticmethod
	# def get_used_wzcards(order_id):
	# 	"""
	# 	根据订单号查微众卡信息
	# 	"""
	# 	used_wzcards = []
	# 	logs = wzcard_models.WeizoomCardHasOrder.select().dj_where(order_id=order_id)
	# 	for log in logs:
	# 		# 三元组表示：card_id, money, last_status
	# 		# TODO: 待重构（相当于这里知道了WZCardResource的细节）
	#
	# 		# 将wzcard.id转成wzcard_id
	# 		wzcard = WZCard.from_id({'id': log.card_id})
	# 		if wzcard:
	# 			# 因为没有存储微众卡回滚之前的状态，这里只能设个默认值
	# 			# TODO: 后续改成根据微众卡金额判断状态
	# 			default_wzcard_status = wzcard_models.WEIZOOM_CARD_STATUS_USED
	# 			used_wzcards.append( (wzcard.wzcard_id, log.money, default_wzcard_status) )
	# 	return used_wzcards
	#
	# @staticmethod
	# def remove_wzcard_logs_by_order_id(order_id):
	# 	"""
	# 	删除order_id所用的WZCard
	#
	# 	@todo 整合至WZCard.refund()
	# 	"""
	# 	records = wzcard_models.WeizoomCardHasOrder.delete().dj_where(order_id=order_id).execute()
	# 	logging.warning("REMOVED wzcard logs. order_id: {}, result: {}".format(order_id, records))
	# 	return

