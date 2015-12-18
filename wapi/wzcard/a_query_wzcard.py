# -*- coding: utf-8 -*-
"""@package wapi.wzcard.a_query_wzcard
微众卡查询\创建
"""

#import copy
#from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
#from db.mall import models as mall_models
#from db.mall import promotion_models
#from db.wzcard import models as wzcard_models
from business.wzcard.wzcard import WZCard
from utils import dateutil as utils_dateutil
import logging
#import resource
#from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
#from core.cache import utils as cache_utils
#from business.mall.order_factory import OrderFactory
#from business.mall.purchase_info import PurchaseInfo
#from business.mall.pay_interface import PayInterface
import logging

from business.wzcard.wzcard_resource_allocator import WZCardChecker

class AQueryWZCard(api_resource.ApiResource):
	"""
	校验微众卡信息（用于user_center）
	"""
	app = 'wzcard'
	resource = 'query_wzcard'

	@param_required(['woid', 'wzcard_id', 'password'])
	def get(args):
		"""
		校验微众卡信息
		"""
		webapp_owner = args['webapp_owner']
		wzcard_id = args['wzcard_id']
		wzcard_password = args['password']

		# 获取微众卡信息
		wzcard = WZCard.from_wzcard_id({
				"webapp_owner": webapp_owner,
				"wzcard_id": args['wzcard_id'],
			})

		checker = WZCardChecker()
		is_success, reason = checker.check(wzcard_id, wzcard_password, wzcard)

		# TODO: 是不是这些信息放在Web端比较好呢？
		if not is_success:
			if 'wzcard:nosuch' == reason['type']:
				msg = u'卡号或密码错误'
			else:
				msg = reason['msg']
			return {
				'code': 400,
				'type': reason['type'],
				'msg': msg
			}

		msg = None
		if wzcard.is_empty:
			msg = u'您的微众卡余额不足!'

		return {
			'code': 200,
			'readable_status': wzcard.readable_status,
			'status': wzcard.status,
			'balance': wzcard.balance,
			'msg': msg
		}
