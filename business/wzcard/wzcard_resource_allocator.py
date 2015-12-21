#coding: utf8
"""@package business.wzcard.wzcard_resource_allocator
微众卡资源分配器
"""

from business import model as business_model
import logging
from business.wzcard.wzcard import WZCard
from business.wzcard.wzcard_resource import WZCardResource
from business.wzcard.wzcard_checker import WZCardChecker
from decimal import Decimal


# 每单用微众卡数量
MAX_WZCARD_PER_ORDER = 10



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

		webapp_owner = self.__webapp_owner

		used_wzcards = []
		total_used_amount = Decimal(0)

		# 检查每单用微众卡数量，是否超过10张
		# @see  `def check_weizoom_card_for_order()`
		if len(wzcard_info_list) > MAX_WZCARD_PER_ORDER:
			reason = {
				"is_success": False,
				"type": 'wzcard:exceeded',
				"msg": u'微众卡只能使用十张',
				"short_msg": u'卡未激活'
			}			
			return False, reason, None

		checker = WZCardChecker()
		# 遍历微众卡信息，扣除微众卡
		for wzcard_info in wzcard_info_list:
			# 根据wzcard_info获取wzcard对象
			wzcard_id = wzcard_info['card_name']
			wzcard_password = wzcard_info['card_pass']
			wzcard = WZCard.from_wzcard_id({
				#"webapp_owner": webapp_owner,
				"wzcard_id": wzcard_id,
				})
			logging.info("wzcard_id: {}, wzcard: {}".format(wzcard_id, wzcard))
			
			is_success, reason = checker.check(wzcard_id, wzcard_password, wzcard)

			if is_success:
				# 验证微众卡可用
				used_amount = wzcard.pay(order.final_price)
				logging.info("order.final_price={}, used_amount={}".format(order.final_price, used_amount))

				# 保存微众卡使用的信息，完成扣除微众卡金额动作
				wzcard.save()
				total_used_amount += used_amount

				# 保存微众卡号、使用金额
				used_wzcards.append( (wzcard, used_amount) )
			else:
				break

		if is_success:
			# TODO: 需要将order.final_price改成Decimal
			order.final_price -= float(total_used_amount)
			order.weizoom_card_money = total_used_amount
			# 分配WZCardResource
			wzcard_resource = WZCardResource(
				self.resource_type,
				[(item[0].wzcard_id, item[1]) for item in used_wzcards]
				)
			logging.info("total_used_amount: {}, order.final_price: {}".format(total_used_amount, order.final_price))
		else:
			# 退还微众卡
			for item in used_wzcards:
				wzcard = item[0]
				used_amount = item[1]
				wzcard.refund(used_amount)
			wzcard_resource = None
			order.weizoom_card_money = Decimal(0)
			
		return is_success, reason, wzcard_resource


	def release(self, resource):
		"""
		释放微众卡资源

		@param resource 由此allocator分配的微众卡资源
		@note 退回微众卡账户
		@todo 待实现
		"""
		logging.info("calling WZCardResourceAllocator.release() to release resources, resource: {}".format(resource))
		if isinstance(resource, WZCardResource):
			used_wzcards = resource.used_wzcards
			# 退回扣款记录
			for wzcard_id, used_amount in used_wzcards:
				# 找到对应的卡
				wzcard = WZCard.from_wzcard_id({
					"webapp_owner": self.__webapp_owner,
					"wzcard_id": wzcard_id,
					})
				# 退款
				is_success, balance = wzcard.refund(used_amount, u'refund')
				# TODO: 如果退款失败怎么办？
				logging.info("WZCard refunded: is_success: {}, balance: {}".format(is_success, balance))
		return

	@property
	def resource_type(self):
		return "wzcard"
