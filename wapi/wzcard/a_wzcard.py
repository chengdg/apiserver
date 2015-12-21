# -*- coding: utf-8 -*-
"""@package wapi.wzcard.a_wzcard
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
#from utils import dateutil as utils_dateutil
import logging
#import resource
#from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
#from core.cache import utils as cache_utils
#from business.mall.order_factory import OrderFactory
#from business.mall.purchase_info import PurchaseInfo
#from business.mall.pay_interface import PayInterface

class AWZCard(api_resource.ApiResource):
	"""
	微众卡
	"""
	app = 'wzcard'
	resource = 'wzcard'

	@param_required(['wzcard_id'])
	def get(args):
		"""
		获取微众卡信息
		"""
		#webapp_owner = args['webapp_owner']
		# 获取微众卡信息
		card = WZCard.from_wzcard_id({
				#"webapp_owner": webapp_owner,
				"wzcard_id": args['wzcard_id'],
			})
		return {
			'readable_status': card.readable_status,
			'status': card.status,
			'balance': card.balance,
		}


	@param_required(['woid', 'wzcard_id', 'password', 'balance', 'status'])
	def put(args):
		"""
		创建微众卡

		@param woid WebAppOwnerId
		@param wzcard_id 微众卡ID
		@param password 微众卡密码
		@param balance 微众卡金额

		"""
		#webapp_owner = args['webapp_owner']
		return {}	
