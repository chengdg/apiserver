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

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
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

	@staticmethod
	def release(resources):
		#TODO-bert
		for_release_resources = []
		for resource in resources:
			if resource.get_type() == business_model.RESOURCE_TYPE_INTEGRAL:
				for_release_resources.append(resource)

		for resource in for_release_resources:
			resource.release()

	def allocate_resource(self, integral):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		count_per_yuan = webapp_owner.integral_strategy_settings.integral_each_yuan
		total_integral = 0
		integral_money = 0

		integral_resource = IntegralResource.get({
					'type': business_model.RESOURCE_TYPE_INTEGRAL,
					'webapp_user': webapp_user,
					'webapp_owner': webapp_owner
				})

		successed,reason = integral_resource.get_resource(integral)

		if successed:
			return True, '', integral_resource
		else:
			return False, reason, None
