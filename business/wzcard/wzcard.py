# coding: utf8
"""@package business.wzcard.wzcard_checker
微众卡检查器

判断微众卡是否能用、是否有效、是否激活等各种情况。
"""

import db.mall.models as mall_models
import settings
from util.microservice_consumer import microservice_consume2


class WZCard(object):
	"""
	微众卡操作业务模型
	"""

	def __init__(self, webapp_user, webapp_owner):
		self.webapp_user = webapp_user
		self.webapp_owner = webapp_owner

	def __get_webapp_user_info(self):
		"""
		微众卡相关的用户信息
		@return:
		"""
		# customer_type 使用者类型(普通会员：0、会员首单：1、非会员：2)
		if self.webapp_user.member.is_subscribed:
			if mall_models.Order.select().dj_where(webapp_user_id=self.webapp_user.id).count() > 0:
				customer_type = 0
			else:
				customer_type = 1
		else:
			customer_type = 2

		return {
			'customer_type': customer_type,
			'customer_id': self.webapp_user.member.id,
		}

	def __get_webapp_owner_info(self):
		"""
		微众卡相关的商户信息
		@return:
		"""
		return {
			'shop_id': self.webapp_owner.id,
			'shop_name': self.webapp_owner.user_profile.store_name,
		}

	def check(self, args):
		"""
		检查微众卡，编辑订单页接口使用
		@type args: h5请求参数
		"""
		data = {
			'card_number': args['card_number'],
			'card_password': args['card_password'],
			'exist_cards': args['exist_cards'],
			'valid_money': args['valid_money'],  # 商品原价+运费
		}

		data.update(self.__get_webapp_owner_info())
		data.update(self.__get_webapp_user_info())

		url = "http://" + settings.CARD_SERVER_DOMAIN + '/card/api/check'

		print('-----data',data)
		print('-----url',url)


		is_success, resp = microservice_consume2(url=url, data=data, method='post')

		return is_success, resp

	def use(self, wzcard_info, money, valid_money, order_id):
		"""
		使用微众卡，下单接口使用
		@param wzcard_info:
		@param money:
		@param valid_money:
		@param order_id:
		@return:
		"""
		data = {
			'card_infos': wzcard_info,
			'money': money,
			'valid_money': valid_money,
			'order_id': order_id
		}

		data.update(self.__get_webapp_owner_info())
		data.update(self.__get_webapp_user_info())

		url = "http://" + settings.CARD_SERVER_DOMAIN + '/card/api/use'
		is_success, resp = microservice_consume2(url=url, data=data, method='post')

		return is_success, resp

	def boring_check(self, card_numbers):
		"""
		1. 检查重复使用
		2. 一个订单只能有10张微众卡
		@param card_numbers: 卡号列表
		@return:
		"""
		if len(card_numbers) > 10:
			return False, "微众卡只能使用十张"
		elif len(card_numbers) > len(set(card_numbers)):
			return False, "该微众卡已经添加"
		else:
			return True, ""

	def refund(self, order_id, trade_id):
		"""
		微众卡退款，取消订单或者下单失败时使用
		@param order_id:
		@param trade_id:
		@return:
		"""
		# 交易类型（支付失败退款：0、普通退款：1）
		if mall_models.Order.select().dj_where(order_id=order_id).first():
			trade_type = 1
		else:
			trade_type = 0
		data = {
			'trade_id': trade_id,
			'trade_type': trade_type
		}

		url = "http://" + settings.CARD_SERVER_DOMAIN + '/card/api/refund'
		is_success, resp = microservice_consume2(url=url, data=data, method='post')

		return is_success, resp

	# @staticmethod
	# def check_not_duplicated(wzcard_info_list):
	# 	"""
	# 	检查微众卡号是否重复
	# 	"""
	#
	# 	if len(wzcard_info_list) == 0:
	# 		return True, {}
	#
	# 	# SELECT count(*) FROM weapp.market_tool_weizoom_card as card join market_tool_weizoom_card_rule as rule on (card.weizoom_card_rule_id=rule.id) where card.weizoom_card_id in ('0000001','0000002','0000021') and rule.valid_restrictions >0;
	# 	wzcard_id_ids = [wzcard_info['card_name'] for wzcard_info in wzcard_info_list]
	# 	valid_restrictions_card_count = wzcard_models.WeizoomCard.select().join(wzcard_models.WeizoomCardRule).where(wzcard_models.WeizoomCard.weizoom_card_id.in_(wzcard_id_ids),wzcard_models.WeizoomCardRule.valid_restrictions >0).count()
	# 	if valid_restrictions_card_count > 1:
	# 		return False, {
	# 				"is_success": False,
	# 				"type": 'coupon',
	# 				"msg": '只可使用一张满额使用卡',
	# 				"short_msg": u'已添加'
	# 			}
	#
	# 	id_set = set()
	# 	for wzcard_info in wzcard_info_list:
	# 		wzcard_id = wzcard_info['card_name']
	# 		if wzcard_id in id_set:
	# 			reason = u'该微众卡已经添加'
	# 			logging.error("{}, wzcard_info: {}".format(reason, wzcard_info))
	# 			return False, {
	# 				"is_success": False,
	# 				"type": 'wzcard:duplicated',
	# 				"msg": reason,
	# 				"short_msg": u'已添加'
	# 			}
	# 		id_set.add(wzcard_id)
	# 	return True, {}
	#
	# def check(self, wzcard_id, password, wzcard, webapp_owner, webapp_user,wzcard_check_money):
	# 	"""
	# 	检查微众卡是否可用
	#
	# 	@return 返回二元组：是否可用(True/False), reason。
	#
	# 	其中reason格式：
	# 		{
	# 			"is_success": False,
	# 			"type": 'wzcard:duplicated',
	# 			"msg": reason,
	# 			"short_msg": u'已添加'
	# 		}
	#
	# 	@see `wezoom_card/module_api.py`中的`check_weizoom_card`
	# 	"""
	# 	if wzcard_id in self.checked_wzcard:
	# 		reason = u'该微众卡已经添加'
	# 		logging.error("{}, wzcard: {}".format(reason, wzcard))
	# 		return False, {
	# 			"is_success": False,
	# 			"type": 'wzcard:duplicated',
	# 			"msg": reason,
	# 			"short_msg": u'已添加'
	# 		}
	#
	# 	self.checked_wzcard[wzcard_id] = wzcard
	#
	# 	member = webapp_user.member
	# 	owner_id =webapp_owner.id
	# 	msg = ''
	#
	# 	if wzcard:
	# 		weizoom_card_rule = wzcard_models.WeizoomCardRule.select().dj_where(id=wzcard.weizoom_card_rule_id).first()
	# 		rule_id = weizoom_card_rule.id
	# 	else:
	# 		weizoom_card_rule =None
	# 		rule_id = None
	#
	# 	if not wzcard:
	# 		# 无此微众卡
	# 		reason = u'卡号或密码错误'
	# 		logging.error("{}, wzcard: {}".format(reason, wzcard))
	# 		return False, {
	# 			"is_success": False,
	# 			"type": 'wzcard:nosuch',
	# 			"msg": reason,
	# 			"short_msg": u'无此卡'
	# 		}
	# 	elif not wzcard.check_password(password):
	# 		# 密码错误
	# 		reason = u'卡号或密码错误'
	# 		logging.error("{}, wzcard: {}".format(reason, wzcard))
	# 		return False, {
	# 			"is_success": False,
	# 			"type": 'wzcard:wrongpass',
	# 			"msg": reason,
	# 			"short_msg": u'密码错误'
	# 		}
	# 	elif wzcard.is_expired:
	# 		# 密码错误
	# 		reason = u'微众卡已过期'
	# 		logging.error("{}, wzcard: {}".format(reason, wzcard))
	# 		return False, {
	# 			"is_success": False,
	# 			"type": 'wzcard:expired',
	# 			"msg": reason,
	# 			"short_msg": u'微众卡已过期'
	# 		}
	# 	elif not wzcard.is_activated:
	# 		reason = u'微众卡未激活'
	# 		logging.error("{}, wzcard: {}".format(reason, wzcard))
	# 		return False, {
	# 			"is_success": False,
	# 			"type": 'wzcard:inactive',
	# 			"msg": reason,
	# 			"short_msg": u'卡未激活'
	# 		}
	# 	elif weizoom_card_rule.valid_restrictions > 0:
	# 		if Decimal(wzcard_check_money) < weizoom_card_rule.valid_restrictions:
	# 			msg = u'订单未满足该卡使用条件'
	# 	elif weizoom_card_rule.card_attr:
	# 		#专属卡
	# 		#是否为新会员专属卡
	# 		#多专属商家id
	# 		shop_limit_list = str(weizoom_card_rule.shop_limit_list).split(',')
	# 		#多黑名单商家id
	# 		shop_black_list = str(weizoom_card_rule.shop_black_list).split(',')
	#
	# 		if weizoom_card_rule.is_new_member_special:
	# 			if member and member.is_subscribed:
	# 				# 防止循环引用
	# 				from business.mall.order import Order
	# 				orders = Order.get_orders_for_webapp_user({'webapp_owner': webapp_owner, 'webapp_user': webapp_user})
	# 				has_order = len(orders)
	# 				#判断是否首次下单
	# 				if has_order:
	# 					order_ids = [order.order_id for order in orders]
	# 					#不是首次下单，判断该卡是否用过
	# 					has_use_card = wzcard_models.WeizoomCardHasOrder.select().dj_where(card_id=wzcard.id, order_id__in=order_ids).count()>0
	# 					if not has_use_card:
	# 						msg = u'该卡为新会员专属卡'
	#
	# 				if str(owner_id) in shop_limit_list:
	# 					if str(owner_id) in shop_black_list:
	# 						msg = u'该卡不能在此商家使用'
	#
	# 				else:
	# 					msg = u'该专属卡不能在此商家使用'
	# 			else:
	# 				if str(owner_id) in shop_black_list:
	# 					msg = u'该卡不能在此商家使用'
	# 				else:
	# 					msg = u'该卡为新会员专属卡'
	#
	# 		else:
	# 			if str(owner_id) in shop_limit_list:
	# 				if str(owner_id) in shop_black_list:
	# 					msg = u'该卡不能在此商家使用'
	# 			else:
	# 				msg = u'该专属卡不能在此商家使用'
	#
	# 	elif owner_id and not weizoom_card_rule.card_attr:
	# 		#不是专属卡，但有黑名单
	# 		shop_black_list = str(weizoom_card_rule.shop_black_list).split(',')
	# 		if str(owner_id) in shop_black_list:
	# 			msg = u'该卡不能在此商家使用'
	#
	# 	elif owner_id and rule_id in [23, 36] and owner_id != 157:
	# 		if '吉祥大药房' in wzcard.weizoom_card_rule.name:
	# 			msg = u'抱歉，该卡仅可在吉祥大药房微站使用！'
	# 	elif owner_id and rule_id in [99,] and owner_id != 474:
	# 		if '爱伲' in wzcard.weizoom_card_rule.name:
	# 			msg = u'抱歉，该卡仅可在爱伲咖啡微站使用！'
	#
	# 	if msg:
	# 		return False, {
	# 			"is_success": False,
	# 			"type": 'wzcard:banned',
	# 			"msg": msg,
	# 			"short_msg": u'规则禁用的微众卡'
	# 		}
	#
	# 	return True, {}



	#
	#
	# elif owner_id and weizoom_card_rule.card_attr:
	# 	#专属卡
	# 	#是否为新会员专属卡
	# 	mpuser_name = u''
	# 	authed_appid = ComponentAuthedAppidInfo.objects.filter(auth_appid__user_id=weizoom_card_rule.belong_to_owner)
	# 	if authed_appid.count()>0:
	# 		if authed_appid[0].nick_name:
	# 			mpuser_name = authed_appid[0].nick_name
	# 	if weizoom_card_rule.is_new_member_special:
	# 		if member and member.is_subscribed:
	# 			orders = belong_to(webapp_id)
	# 			orders = orders.filter(webapp_id=webapp_id,webapp_user_id=webapp_user.id).exclude(status=ORDER_STATUS_CANCEL)
	# 			has_order = orders.count() >0
	# 			#判断是否首次下单
	# 			if has_order:
	# 				order_ids = [order.order_id for order in orders]
	# 				#不是首次下单，判断该卡是否用过
	# 				has_use_card = WeizoomCardHasOrder.objects.filter(card_id=weizoom_card.id,order_id__in=order_ids).count()>0
	# 				if not has_use_card:
	# 					msg = u'该卡为新会员专属卡'
	# 			if owner_id != weizoom_card_rule.belong_to_owner:
	# 				msg = u'该卡为'+mpuser_name+'商家专属卡'
	# 		else:
	# 			msg = u'该卡为新会员专属卡'
	# 	else:
	# 		if owner_id != weizoom_card_rule.belong_to_owner:
	# 			msg = u'该卡为'+mpuser_name+'商家专属卡'
	# elif owner_id and rule_id in [23, 36] and owner_id != 157:
	# 	WeizoomCardRule.objects.get(id=rule_id)
	# 	if '吉祥大药房' in weizoom_card.weizoom_card_rule.name:
	# 		msg = u'抱歉，该卡仅可在吉祥大药房微站使用！'
	# elif owner_id and rule_id in [99,] and owner_id != 474:
	# 	WeizoomCardRule.objects.get(id=rule_id)
	# 	if '爱伲' in weizoom_card.weizoom_card_rule.name:
	# 		msg = u'抱歉，该卡仅可在爱伲咖啡微站使用！'
	# # else:
