# coding: utf8
"""@package business.wzcard.wzcard_resource_allocator
微众卡资源分配器

"""

import logging
import json
from business import model as business_model
from business.member_card.member_card import MemberCard
from db.mall import models as mall_models
# 每单用微众卡数量
from business.member_card.member_card_resource import MemberCardResource
from business.wzcard.wzcard import WZCard

MAX_WZCARD_PER_ORDER = 10


class MemberCardResourceAllocator(business_model.Service):
	"""
	会员卡资源分配器

	
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
		分配微众卡资源

		@param[in] order 订单对象
		@param[in] purchase_info 订单信息。其中的`member_card_price`存放会员卡使用金额。

		**分配资源流程**：
			1. 获取微众卡信息；
			2. 除微众卡金额；
			3. 返回微众卡资源(MemberCardResource)对象

		@todo 应该先抽取微众卡资源，然后判断是否有效，再执行扣资源的操作
		"""
		logging.info("type of `order`: {}".format(type(order)))
		should_use_member_card = purchase_info.member_card_price > 0 and order.final_price > 0
		if not should_use_member_card or not self.__webapp_user.member_card:
			return True, [], None
		valid_money = order.postage + sum(
			[product.original_price * product.purchase_count for product in order.products])

		# usable_member_card_info =  [
		# 	{'card_number': self.__webapp_user.member_card.card_number, 'card_password': MemberCard.decrypt_password(self.__webapp_user.member_card.card_password)} ]
		usable_member_card_info =  [
			{'card_number': self.__webapp_user.member_card.card_number, 'card_password': self.__webapp_user.member_card.card_password} ]

		can_use, msg, data = MemberCard.use({
			'wzcard_info': usable_member_card_info,
			'money': order.final_price,
			'order_id': order.order_id,
			'webapp_user': self.__webapp_user,
			'webapp_owner': self.__webapp_owner
		})

		if can_use:
			paid_money = float(data['paid_money'])
			# todo 优化到package_order_service
			order.final_price -= paid_money
			order.member_card_money = paid_money
			member_card_resource = MemberCardResource(self.resource_type, order.order_id, data['trade_id'], self.__webapp_user.member_card.id, paid_money)
			return True, [], member_card_resource
		else:
			# 处理余额为0的微众卡
			if data.get('type', '') == 'wzcard:use_up':
				return True, [], None

			reason = {
				"is_success": False,
				"type": data['type'],
				"msg": u"会员卡无法使用",
				"short_msg": u"会员卡无法使用"
			}
			return False, [reason], None


	def release(self, resource):
		"""
		释放微众卡资源

		@param[in] resource 由此allocator分配的微众卡资源
		@note 退回微众卡账户
		@todo 退款记录
		"""
		logging.info("calling MemberCardResourceAllocator.release() to release resources, resource: {}".format(resource))
		order_id = resource.order_id
		trade_id = resource.trade_id

		is_success = MemberCard.refund({'order_id': order_id, 'trade_id': trade_id, 'member_card_id': resource.member_card.id, 'price': resource.price})
		# TODO: 如果退款失败怎么办？
		return is_success

	@property
	def resource_type(self):
		"""
		资源类型标识符（作为分配MemberCardResource的一个参数）
		"""
		return "member_card"

	