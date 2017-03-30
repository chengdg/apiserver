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
		"""
		logging.info("type of `order`: {}".format(type(order)))
		should_use_card = purchase_info.jinge_card_price > 0 and order.final_price > 0
		if not should_use_card:
			return True, [], None

		is_success, trade_id = self.__webapp_user.jinge_card.use(order.order_id, purchase_info.jinge_card_price)

		if is_success:
			paid_money = purchase_info.jinge_card_price
			order.final_price -= paid_money
			order.third_party_money = paid_money
			jinge_card_resource = JinGeCardResource(self.resource_type, order.order_id, trade_id, paid_money)
			return True, [], jinge_card_resource
		else:
			return False, [], None


	def release(self, resource):
		"""
		释放锦歌饭卡资源
		"""
		logging.info("calling JinGeCardResourceAllocator.release() to release resources, resource: {}".format(resource))
		order_id = resource.order_id
		trade_id = resource.trade_id
		trade_id = resource.money
		is_success = self.__webapp_user.refund(order_id, trade_id, money)
		# TODO: 如果退款失败怎么办？
		return is_success

	@property
	def resource_type(self):
		"""
		资源类型标识符
		"""
		return "jinge_card"
