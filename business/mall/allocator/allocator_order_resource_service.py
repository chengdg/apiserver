# -*- coding: utf-8 -*-
"""@package business.mall.allocator.allocator_order_resource_service.AllocateOrderResourceService
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
from business.mall.allocator.order_integral_resource_allocator import OrderIntegralResourceAllocator
from business.mall.allocator.order_product_resource_allocator import OrderProductResourceAllocator
from business.mall.allocator.order_coupon_resource_allocator import OrderCouponResourceAllocator


class AllocateOrderResourceService(business_model.Service):

	"""
	AllocateOrderResourceService
	"""
	allocators = [
		OrderIntegralResourceAllocator,
		OrderProductResourceAllocator,
		OrderCouponResourceAllocator
	]

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['allocators'] = [allocator(webapp_owner, webapp_user) for allocator in AllocateOrderResourceService.allocators]

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

	def allocate_resource_for(self, order, purchase_info):
		resources = []
		is_success = True
		reasons = []
		for allocator in self.context['allocators']:
			#积分: {'type': 'integral', 'integral': 5, 'integral_money': 10}
			is_success, reason, resource = allocator.allocate_resource(order, purchase_info)
			if not is_success:
				reasons.append(reason)
				self.release(resources)
				break
			else:
				if isinstance(resource,list):
					resources.extend(resource)
				else:
					resources.append(resource)
		
		return is_success, reasons, resources

	def release(self, resources):
		if not resources:
			return 
		for allocator in self.context['allocators']:
			allocator.release(resources)
