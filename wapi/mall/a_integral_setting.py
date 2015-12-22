# -*- coding: utf-8 -*-
"""@package wapi.mall.a_integral_setting
积分配置API

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
from business.account.integral import Integral


class AIntegralSetting(api_resource.ApiResource):
	"""
	积分配置信息
	"""
	app = 'mall'
	resource = 'integral_setting'


	@param_required(['webapp_owner', 'webapp_user'])
	def get(args):

		integral = Integral.from_webapp_id({
					'webapp_owner': args['webapp_owner'], 
					})

		return {
			'integral_strategy_setting': integral.to_dict()
		}