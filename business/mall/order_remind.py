# -*- coding: utf-8 -*-
"""@package business.mall.order_remind
订单提醒/催单
"""
from datetime import datetime

from eaglet.core import watchdog
from eaglet.decorator import param_required
from bdem import msgutil

from business import model as business_model
from business.mall.order import Order
from business.mall.product_review import ProductReview
from db.mall import models as mall_models


class OrderRemind(business_model.Model):
	__slots__ = (
	)

	@staticmethod
	@param_required(['webapp_id', 'order_id'])
	def create(args):
		"""
		创建催单记录并发送催单短信
		"""
		watchdog.info("to create an OrderRemind...")
		order_id = args['order_id']
		webapp_id = args['webapp_id']

		can_remind = False

		order = mall_models.Order.get(webapp_id=webapp_id, order_id=order_id)
		if order.status == mall_models.ORDER_STATUS_PAYED_NOT_SHIP:
			can_remind = True
		else:
			watchdog.info(u"order: %s不是待发货状态，不能催单" % order.order_id)
			return False

		now = datetime.now()
		delta_hour = (now - order.created_at).days * 24 + (now - order.created_at).seconds / 60 / 60
		if delta_hour < 48:
			watchdog.info(u"order: %s下单不足48小时，不能催单" % order.order_id)
			can_remind = False

		logs = mall_models.OrderOperationLog.select().dj_where(order_id=order_id, action=u'催单')
		last_remind_time = None  #最近一次催单的时间
		remind_history = []
		for log in logs:
			last_remind_time = log.created_at
			created_at = log.created_at.strftime('%m-%d %H:%M')
			remind_history.append(created_at)

		remind_times = len(remind_history)
		if remind_times > 0:
			delta_hour = (now - last_remind_time).days * 24 + (now - last_remind_time).seconds / 60 / 60 #上次催单到现在的小时数
			if remind_times == 1:  #第一次催单12小时后可允许操作第二次催单
				if delta_hour < 12:
					watchdog.info(u"order: %s距离第一次催单不足12小时，不能催单，上次催单时间: %s" % (order.order_id, last_remind_time.strftime('%Y-%m-%d %H:%M:%S')))
					can_remind = False
			elif remind_times == 2:  #第二次催单6小时后可允许第三次催单
				if delta_hour < 6:
					watchdog.info(u"order: %s距离第二次催单不足6小时，不能催单，上次催单时间: %s" % (order.order_id, last_remind_time.strftime('%Y-%m-%d %H:%M:%S')))
					can_remind = False
			elif remind_times >= 3:  #催单不能超过三次
				watchdog.info(u"order: %s已经催单3次，不能再催单，上次催单时间: %s" % (order.order_id, last_remind_time.strftime('%Y-%m-%d %H:%M:%S')))
				can_remind = False

		if can_remind:
			log = mall_models.OrderOperationLog.create(
					order_id=order_id,
					action=u'催单',
					operator=u'客户',
					remark=''
				)

			sub_orders = mall_models.Order.select().dj_where(webapp_id=webapp_id, origin_order_id=order.id, status=mall_models.ORDER_STATUS_PAYED_NOT_SHIP)
			for sub_order in sub_orders:
				supplier_id = sub_order.supplier
				supplier = mall_models.Supplier.get(id=supplier_id)

				sub_order_id = sub_order.order_id
				mall_models.OrderOperationLog.create(
					order_id=sub_order_id,
					action=u'催单',
					operator=u'客户',
					remark=supplier.name
				)
				#发短信
				data = {
					"phones": str(supplier.supplier_tel),
					"content": {
						"order_id": sub_order.order_id,
						"name": sub_order.ship_name
					},
					"sms_code": "SMS_48635069"  #阿里云用户催单提醒模板
				}
				result = msgutil.send_message('notify', 'phone', data)
				if result:
					watchdog.info(u"发送催单短信成功，订单号：{}，手机号：{}，供货商：{}".format(sub_order.order_id, supplier.supplier_tel, supplier.name))
				else:
					watchdog.alert(u"发送催单短信失败，订单号：{}，手机号：{}，供货商：{}".format(sub_order.order_id, supplier.supplier_tel, supplier.name))

			return True
		return False