# -*- coding: utf-8 -*-
"""@package wapi.mall.a_global_navbar
全局导航信息

"""

#import copy
#from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
#from db.mall import models as mall_models
#from db.mall import promotion_models
#from utils import dateutil as utils_dateutil
#import resource
#from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
#from core.cache import utils as cache_utils
#from business.mall.order_factory import OrderFactory
#from business.mall.purchase_info import PurchaseInfo
#from business.mall.pay_interface import PayInterface
import logging
#from core.watchdog.utils import watchdog_info




class AGlobalNavbar(api_resource.ApiResource):
	"""
	全局导航信息

	@see 原始源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
	"""
	app = 'mall'
	resource = 'global_navbar'


	@param_required(['woid'])
	def get(args):
		webapp_owner = args['webapp_owner']
		global_navbar = webapp_owner.global_navbar
		return {
			'is_enable': global_navbar.is_enable,
			'webapp_owner_id': global_navbar.owner_id
		}
		return webapp_owner.global_navbar.to_dict()
