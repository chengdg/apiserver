# -*- coding: utf-8 -*-
"""@package business.mall.allocator.order_integral_resource_allocator.OrderIntegralResourceAllocator
请求积分资源

"""
import logging
import json
from bs4 import BeautifulSoup
import math
import itertools
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from eaglet.core import watchdog
from business import model as business_model 
from business.mall.product import Product
from business.account.integral import Integral
from business.resource.integral_resource import IntegralResource
import settings
from business.decorator import cached_context_property


class IntegralResourceAllocator(business_model.Service):
	"""积分申请器
	"""
	__slots__ = ()

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		#self.context['resource'] = None

	
	def release(self, release_resource=None):
		webapp_user = self.context['webapp_user']
		#release_resource = self.context['resource']
		# release_resources = []
		# for resource in resources:
		# 	if resource.get_type() == business_model.RESOURCE_TYPE_INTEGRAL:
		# 		release_resources.append(resource)

		if release_resource:
			integral = release_resource.integral
			integral_log_id = release_resource.integral_log_id
			if integral_log_id >= 0:
				# 表示积分回滚
				if integral > 0:
					Integral.roll_back_integral({
							'webapp_user': webapp_user,
							'integral_count': integral,
							'integral_log_id': integral_log_id
							})
			else:
				# integral_log_id=-1 表示积分返还
				Integral.return_integral({
							'webapp_user': webapp_user,
							'return_count': integral,
					})
		return


	def allocate_resource(self, integral):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		count_per_yuan = webapp_owner.integral_strategy_settings.integral_each_yuan
		total_integral = 0
		integral_money = 0
		integral_resource = IntegralResource.get({
					'type': self.resource_type,
					'webapp_user': webapp_user,
					'webapp_owner': webapp_owner
				})
		successed,reason = integral_resource.get_resource(integral)

		if successed:
			#self.context['resource'] = integral_resource
			return True, '', integral_resource
		else:
			return False, {
				"is_success": False,
				"type": 'integral',
				"msg": reason,
				"short_msg": reason
			}, None

	@property
	def resource_type(self):
		return business_model.RESOURCE_TYPE_INTEGRAL
