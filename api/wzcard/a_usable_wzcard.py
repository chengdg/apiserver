# -*- coding: utf-8 -*-
"""@package apiwzcard.a_usable_wzcard
微众卡查询\创建
"""

#import copy
#from datetime import datetime

from eaglet.core import api_resource
from eaglet.decorator import param_required
#from db.mall import models as mall_models
#from db.mall import promotion_models
#from db.wzcard import models as wzcard_models
from business.wzcard.wzcard import WZCard
from util import dateutil as utils_dateutil
import logging
#import resource
#from api.mall.a_purchasing import APurchasing as PurchasingApiResource
#from eaglet.core.cache import utils as cache_utils
#from business.mall.order_factory import OrderFactory
#from business.mall.purchase_info import PurchaseInfo
#from business.mall.pay_interface import PayInterface

from business.wzcard.wzcard_checker import WZCardChecker

class AUsableWZCard(api_resource.ApiResource):
	"""
	可用的微众卡
	"""
	app = 'wzcard'
	resource = 'usable_wzcard'

	@param_required(['wzcard_id', 'password'])
	def get(args):
		"""
		校验微众卡信息
		"""
		#webapp_owner = args['webapp_owner']
		wzcard_id = args['wzcard_id']
		wzcard_password = args['password']
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		used_cards = args.get('used_cards', '')
		used_cards = used_cards.split(',') if used_cards else []

		wzcard_check_money = args['wzcard_check_money']

		# # 获取微众卡信息
		# wzcard = WZCard.from_wzcard_id({
		# 		#"webapp_owner": webapp_owner,
		# 		"wzcard_id": args['wzcard_id'],
		# 	})
		#
		# checker = WZCardChecker()
		#
		# # 检查微众卡列表
		# wzcard_info_list = [{'card_name': card} for card in used_cards]
		# wzcard_info_list.append({'card_name': wzcard_id})
		#
		# is_success, reason = WZCardChecker.check_not_duplicated(wzcard_info_list)
		#
		# if is_success:
		# 	# 检查单张微众卡
		# 	is_success, reason = checker.check(wzcard_id, wzcard_password, wzcard, webapp_owner, webapp_user,wzcard_check_money)
		#
		# if not is_success:
		# 	msg = reason['msg']
		# 	return {
		# 		'code': 400,
		# 		'type': reason['type'],
		# 		'msg': msg
		# 	}
		#
		# msg = None
		# if wzcard.is_empty:
		# 	msg = u'您的微众卡余额不足!'
		#
		# return {
		# 	'id': wzcard.id,
		# 	'code': 200,
		# 	'readable_status': wzcard.readable_status,
		# 	'status': wzcard.status,
		# 	'balance': wzcard.balance,
		# 	'msg': msg
		# }

		exist_cards = args.get('used_cards', '')
		exist_cards = exist_cards.split(',') if exist_cards else []

		request_data = {
			'card_number': args['wzcard_id'],
			'card_password': args['password'],
			'valid_money': args['valid_money'],
			'exist_cards': exist_cards
		}

		checker = WZCardChecker(webapp_user, webapp_owner)

		is_success, reason = checker.check_from_card_service(request_data)
		if is_success:
			return {
				'id': wzcard.id,
				'code': 200,
				'readable_status': wzcard.readable_status,
				'status': wzcard.status,
				'balance': wzcard.balance,
				'msg': msg
			}
		else:
			msg = reason['msg']
			return {
				'code': 400,
				'type': reason['type'],
				'msg': msg
			}