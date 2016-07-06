# coding: utf8
"""@package business.wzcard.wzcard_resource_allocator
微众卡资源分配器

"""

import logging
import json
from business import model as business_model
from business.wzcard.wzcard import WZCard
# from business.wzcard.wzcardutil import WZCardUtil
from db.mall import models as mall_models
# 每单用微众卡数量
from business.wzcard.wzcard_resource import WZCardResource

MAX_WZCARD_PER_ORDER = 10


class WZCardResourceAllocator(business_model.Service):
	"""
	微众卡资源分配器

	@see 原Weapp的`card_api_view.py`和`def weizoom_card_pre_save_order`
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
		@param[in] purchase_info 订单信息。其中的`wzcard_info`存放微众卡信息，是 (card_name, card_pass) 的list。

		**分配资源流程**：
			1. 获取微众卡信息；
			2. 依次扣除微众卡金额；
			3. 返回微众卡资源(WZCardResource)对象

		@todo 应该先抽取微众卡资源，然后判断是否有效，再执行扣资源的操作
		"""
		logging.info("type of `order`: {}".format(type(order)))

		should_use_card = len(purchase_info.wzcard_info) > 0 and order.final_price > 0
		if not should_use_card:
			return True, [], None

		valid_money = order.postage + sum(
			[product.original_price * product.purchase_count for product in order.products])

		# card_numbers = [x['card_number'] for x in purchase_info.wzcard_info]
		card_numbers = purchase_info.wzcard_info

		# is_success, msg = WZCard.boring_check(card_numbers)
		# if not is_success:
		# 	reason = {
		# 		"is_success": False,
		# 		"type": 'wzcard:exceeded',
		# 		"msg": msg,
		# 		"short_msg": msg
		# 	}
		# 	return False, [reason], None

		# 检查是否有重复

		if len(card_numbers) > 10:
			reason = {
				"is_success": False,
				"type": 'wzcard:exceeded',
				"msg": '微众卡只能使用十张',
				"short_msg": '微众卡只能使用十张'
			}
			return False, [reason], None

		if len(card_numbers) != len(set(card_numbers)):
			reason = {
				"is_success": False,
				"type": 'wzcard:wzcard:duplicated',
				"msg": '',
				"short_msg": ''
			}
			return False, [reason], None

		usable_wzcard_info = WZCard.get_by_card_numbers(
			{'webapp_user': self.__webapp_user, 'card_numbers': card_numbers})

		can_use, msg, data = WZCard.use({
			'wzcard_info': usable_wzcard_info,
			'money': order.final_price,
			'order_id': order.order_id,
			'webapp_user': self.__webapp_user,
			'webapp_owner': self.__webapp_owner
		})

		if can_use:
			paid_money = float(data['paid_money'])
			# todo 优化到package_order_service
			order.final_price -= paid_money
			order.weizoom_card_money = paid_money
			wzcard_resource = WZCardResource(self.resource_type, order.order_id, data['trade_id'])
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


		# wzcard_info_list = purchase_info.wzcard_info if order.final_price > 0 else []
		# logging.info("wzcard_info: {}".format(wzcard_info_list))
		#
		# # webapp_owner = self.__webapp_owner
		#
		# used_wzcards = []
		# total_used_amount = Decimal(0)
		#
		# # 检查每单用微众卡数量，是否超过10张
		# # @see  `def check_weizoom_card_for_order()`
		# if len(wzcard_info_list) > MAX_WZCARD_PER_ORDER:
		# 	reason = {
		# 		"is_success": False,
		# 		"type": 'wzcard:exceeded',
		# 		"msg": u'微众卡只能使用十张',
		# 		"short_msg": u'卡未激活'
		# 	}
		# 	return False, [reason], None
		#
		# # 检查是否有重复（避免出现重复后release 资源但不改变wzcard状态）
		# is_success, reason = WZCardChecker.check_not_duplicated(wzcard_info_list)
		# if not is_success:
		# 	return False, [reason], None
		#
		# checker = WZCardChecker()
		# # 遍历微众卡信息，扣除微众卡
		# final_price = Decimal(order.final_price)
		# for wzcard_info in wzcard_info_list:
		# 	# 根据wzcard_info获取wzcard对象
		# 	wzcard_id = wzcard_info['card_name']
		# 	wzcard_password = wzcard_info['card_pass']
		# 	wzcard = WZCard.from_wzcard_id({
		# 		# "webapp_owner": webapp_owner,
		# 		"wzcard_id": wzcard_id,
		# 	})
		# 	logging.info("wzcard_id: {}, wzcard: {}".format(wzcard_id, wzcard))
		#
		# 	wzcard_check_money = order.postage + sum(
		# 		[product.original_price * product.purchase_count for product in order.products])
		#
		# 	is_success, reason = checker.check(wzcard_id, wzcard_password, wzcard, self.__webapp_owner,
		# 	                                   self.__webapp_user, wzcard_check_money)
		# 	logging.info(
		# 		u"wzcard_id:{}, status: {}, price: {}, check_result:{}, reason:{}".format(wzcard.wzcard_id, wzcard.zheg,
		# 		                                                                          wzcard.money, is_success,
		# 		                                                                          reason))
		# 	# 试验发watchdog消息
		# 	watchdog.info(u"wzcard_id:{}, status: {}, price: {}, check_result:{}, reason:{}".format(wzcard.wzcard_id,
		# 	                                                                                        wzcard.readable_status,
		# 	                                                                                        wzcard.money,
		# 	                                                                                        is_success, reason))
		#
		# 	if is_success:
		# 		# 验证微众卡可用
		# 		last_status = wzcard.status
		# 		used_amount = wzcard.pay(final_price)
		# 		logging.info("Use WZCard {}, used_amount={}, final_price={}, last_status={}".format(wzcard.wzcard_id,
		# 		                                                                                    used_amount,
		# 		                                                                                    final_price,
		# 		                                                                                    last_status))
		#
		# 		# 使用的微众卡才产生记录
		# 		if used_amount > 0:
		# 			# 保存微众卡使用的信息，完成扣除微众卡金额动作
		# 			wzcard.save()
		# 			total_used_amount += used_amount
		# 			final_price -= used_amount
		#
		# 			# 保存微众卡号、使用金额、上一次状态
		# 			used_wzcards.append((wzcard, used_amount, last_status))
		# 	else:
		# 		break
		#
		# if is_success:
		# 	# TODO: 需要将order.final_price改成Decimal
		# 	order.final_price -= float(total_used_amount)
		# 	order.weizoom_card_money = total_used_amount
		# 	# 分配WZCardResource
		# 	wzcard_resource = WZCardResource(
		# 		self.resource_type,
		# 		[(item[0].wzcard_id, item[1], item[2]) for item in used_wzcards]
		# 	)
		# 	logging.info("total_used_amount: {}, order.final_price: {}".format(total_used_amount, order.final_price))
		#
		# 	# 记录微众卡消费日志 duhao
		# 	# TODO 这种方式太low了。。。
		# 	for item in used_wzcards:
		# 		wzcard = item[0]
		# 		used_amount = item[1]
		# 		LogOperator.record_wzcard_log(self.__webapp_owner.id, order.order_id, wzcard.id, used_amount)
		# else:
		# 	# 退还微众卡
		# 	for item in used_wzcards:
		# 		wzcard = item[0]
		# 		used_amount = item[1]
		# 		last_status = item[2]
		# 		wzcard.refund(used_amount, None, last_status)
		# 	wzcard_resource = None
		# 	order.weizoom_card_money = Decimal(0)
		#
		# return is_success, [reason], wzcard_resource

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
		资源类型标识符（作为分配WZCardResource的一个参数）
		"""
		return "wzcard"

	def __record_trade_id(self, order_id, trade_id, used_card):
		mall_models.OrderCardInfo.create(order_id=order_id, trade_id=trade_id, used_card=used_card)
