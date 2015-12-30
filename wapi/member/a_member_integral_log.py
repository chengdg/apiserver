# -*- coding: utf-8 -*-
"""@package wapi.member.a_member_integral_log
积分日志API

"""

import copy
from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from utils import dateutil as utils_dateutil
#import resource
from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
from core.cache import utils as cache_utils
from business.mall.order_factory import OrderFactory, OrderException
from business.mall.purchase_info import PurchaseInfo
from business.mall.pay_interface import PayInterface
from business.mall.order import Order
from business.account.integral_logs import IntegralLogs


class AMemberIntegralLog(api_resource.ApiResource):
	"""
	积分日志
	"""
	app = 'member'
	resource = 'integral_log'


	@param_required(['webapp_owner', 'webapp_user'])
	def get(args):

		integral_logs = IntegralLogs.get({
				'webapp_owner': args['webapp_owner'], 
				'webapp_user': args['webapp_user']
				})


		return {
			'integral_logs': integral_logs.integral_logs
		}