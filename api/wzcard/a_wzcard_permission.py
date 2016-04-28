# -*- coding: utf-8 -*-

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
import logging

class AWZCardPermission(api_resource.ApiResource):
	"""
	微众卡权限
	"""
	app = 'wzcard'
	resource = 'wzcard_permission'

	@param_required(['woid'])
	def get(args):
		webapp_owner = args['webapp_owner']
		return {
			'wzcard_enabled': webapp_owner.has_wzcard_permission
		}


	@param_required(['woid', 'enabled'])
	def post(args):
		webapp_owner = args['webapp_owner']
		is_enabled = int(args['enabled']) != 0
		logging.info("is_enabled: {}".format(is_enabled))
		if is_enabled:
			webapp_owner.enable_wzcard_permission()
		else:
			webapp_owner.disable_wzcard_permission()
		return {
			'wzcard_enabled': webapp_owner.has_wzcard_permission
		}
