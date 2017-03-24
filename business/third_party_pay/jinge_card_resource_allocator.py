# coding: utf8
"""@package business.third_party_pay.jinge_card_resource_allocator
锦歌饭卡资源分配器

"""

import logging
import json
from business import model as business_model
from business.third_party_pay.jinge_card import JinGeCard
from db.mall import models as mall_models
from business.third_party_pay.jinge_card_resource import JinGeCardResource

class JinGeCardResourceAllocator(business_model.Service):
	"""
	锦歌饭卡资源分配器
	"""

	__slots__ = (
		'__webapp_owner',
		'__webapp_user',
	)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.__webapp_owner = webapp_owner
		self.__webapp_user = webapp_user

	def __get_empty_resource(self):
		pass

	def allocate_resource(self, order, purchase_info):
		"""
		分配锦歌饭卡资源

		@param[in] order 订单对象
		@param[in] purchase_info 订单信息。其中的`wzcard_info`存放微众卡信息，是 (card_name, card_pass) 的list。

		**分配资源流程**：
			1. 获取微众卡信息；
			2. 依次扣除微众卡金额；
			3. 返回微众卡资源(WZCardResource)对象

		@todo 应该先抽取微众卡资源，然后判断是否有效，再执行扣资源的操作
		"""
		logging.info("type of `order`: {}".format(type(order)))
		should_use_card = purchase_info.jinge_card_price > 0 and order.final_price > 0
		if not should_use_card:
			return True, [], None

		is_success, reason, trade_id = self.__webapp_user.jinge_card.use(order_id, purchase_info.jinge_card_price)

		if is_success:
			paid_money = purchase_info.jinge_card_price
			order.final_price -= paid_money
			order.third_party_money = paid_money
			jinge_card_resource = JinGeCardResource(self.resource_type, order.order_id, trade_id)
			return True, [], wzcard_resource
		else:
			# 处理余额为0的微众卡
			if data.get('type', '') == 'wzcard:use_up':
				return True, [], None

			reason = {
				"is_success": False,
				"type": data['type'],
				"msg": msg,
				"short_msg": msg
			}
			return False, [reason], None


	def release(self, resource):
		"""
		释放微众卡资源

		@param[in] resource 由此allocator分配的微众卡资源
		@note 退回微众卡账户
		@todo 退款记录
		"""
		logging.info("calling WZCardResourceAllocator.release() to release resources, resource: {}".format(resource))
		order_id = resource.order_id
		trade_id = resource.trade_id
		# wzcard = WZCardUtil(self.__webapp_user, self.__webapp_owner)
		is_success = WZCard.refund({'order_id': order_id, 'trade_id': trade_id})
		# TODO: 如果退款失败怎么办？
		return is_success

	@property
	def resource_type(self):
		"""
		资源类型标识符
		"""
		return "jinge_card"

	def __record_trade_id(self, order_id, trade_id, used_card):
		mall_models.OrderCardInfo.create(order_id=order_id, trade_id=trade_id, used_card=used_card)
