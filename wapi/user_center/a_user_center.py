# -*- coding: utf-8 -*-

import copy
from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from wapi.mall import models as mall_models
from wapi.mall import promotion_models
from utils import dateutil as utils_dateutil
import resource
from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
from cache import utils as cache_utils
from business.mall.order_factory import OrderFactory
from business.mall.purchase_info import PurchaseInfo
from business.mall.pay_interface import PayInterface

class AUserCenter(api_resource.ApiResource):
	"""
	个人中心
	"""
	app = 'user_center'
	resource = 'user_center'

	@param_required(['woid'])
	def get(args):
		"""
		获取个人中心
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		data = {
			'info': 'user_center'
		}

		return data