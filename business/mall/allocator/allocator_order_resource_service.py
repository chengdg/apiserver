# -*- coding: utf-8 -*-
"""@package business.mall.order_resource_allocator
订单资源分配器

"""

import json
from bs4 import BeautifulSoup
import math

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.allocator.order_integral_allocator import OrderIntegralAllocator


class AllocateOrderResourceService(business_model.Service):

	"""
	AllocateOrderResourceService
	"""
	allocators = [
		OrderIntegralAllocator
	]

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['allocators'] = [allocator(webapp_owner, webapp_user) for allocator in AllocateOrderResourceService.allocators]

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		self.context['resources'] = []


	def allocate_resource_for(self, order, purchase_info):
		resources = []
		is_success = True
		reason = ''
		for allocator in self.context['allocators']:
			#积分: {'type': 'integral', 'integral': 5, 'integral_money': 10}
			is_success, reason, resource = allocator.allocate_resource(order, purchase_info)
			if not is_success:
				self.release()
				break
			else:
				resources.append(resource)
		
		self.context['resources'] = resources
		return is_success, reason, resources

	def release(self):
		if not self.context['resources']:
			return 
		for allocator in self.context['allocators']:
			allocator.release(self.context['resources'])
