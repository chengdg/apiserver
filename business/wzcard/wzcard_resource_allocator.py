#coding: utf8
"""@package business.wzcard.wzcard_resource_allocator
微众卡资源分配器
"""

from business import model as business_model
import logging
from business.wzcard.wzcard import WZCard
from business.wzcard.wzcard_resource import WZCardResource


class WZCardResourceAllocator(business_model.Service):
	"""
	微众卡资源分配器

	@see 原Weapp的`card_api_view.py`
	@see `def weizoom_card_pre_save_order`
	"""
	__slots__ = (
		'__webapp_owner',
		'__webapp_user',
	)
	
	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.__webapp_owner = webapp_owner
		self.__webapp_user = webapp_user


	def allocate_resource(self, order, purchase_info):
		"""
		分配微众卡资源

		@param order 订单对象
		@param purchase_info 订单信息。其中的`wzcard_info`存放微众卡信息，是`(card_name, card_pass)`的list。

		分配流程：
			1. 获取微众卡信息；
			2. 依次扣除微众卡金额；
			3. 返回微众卡资源(WZCardResource)对象
		"""
		is_success = True
		reason = ''

		logging.info("type of `order`: {}".format(type(order)))

		wzcard_info_list = purchase_info.wzcard_info
		logging.info("wzcard_info: {}".format(wzcard_info_list))

		# TODO: 检查微众卡是否超过10张
		# @see  `def check_weizoom_card_for_order()`

		webapp_owner = self.context['webapp_owner']

		used_wzcards = []
		# 遍历微众卡信息，扣除微众卡
		for wzcard_info in wzcard_info_list:
			# 根据wzcard_info获取wzcard对象
			wzcard = WZCard.from_wzcard_id({
				"webapp_owner": webapp_owner,
				"wzcard_id": wzcard_info['card_name'],
				})

			# 检查微众卡是否可用
			if wzcard and wzcard.check_password(wzcard_info['card_pass']):
				# 验证微众卡可用

				#used_amount = wzcard.pay(order.final_price)
				#logging.info("order.final_price={}, used_amount={}".format(order.final_price, used_amount))

				# 保存微众卡使用的信息，完成扣除微众卡金额动作
				#wzcard.save()

				# 保存微众卡号、使用金额
				if wzcard.balance>1e-3:
					used_wzcards.append([
						wzcard.wzcard_id,
						])
			else:
				# 验证微众卡失败
				is_success = False

		wzcard_resource = WZCardResource('wzcard', used_wzcards)
		return is_success, reason, wzcard_resource


	def release(self, resource):
		"""
		释放微众卡资源

		@param resource 由此allocator分配的微众卡资源
		@note 退回微众卡账户
		@todo 待实现
		"""
		pass
