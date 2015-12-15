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
from business.mall.allocator.order_products_resource_allocator import OrderProductsResourceAllocator
from business.mall.allocator.order_coupon_resource_allocator import OrderCouponResourceAllocator
from business.wzcard.wzcard_resource_allocator import WZCardResourceAllocator

import logging

class AllocateOrderResourceService(business_model.Service):

	"""
	AllocateOrderResourceService
	"""
	#这里的顺序非常重要，OrderProductsResourceAllocator，必须要在OrderIntegralResourceAlloctor之前
	#因为买赠会修改积分应用计算积分金额限额的价格基数（当有买赠时，按原价计算；当没有买赠时，按会员价计算）
	allocators = [
		OrderProductsResourceAllocator,
		OrderIntegralResourceAllocator,
		OrderCouponResourceAllocator,
		#WZCardResourceAllocator,
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
			logging.info("allocating resource using {}".format(allocator))
			is_success, reason, resource = allocator.allocate_resource(order, purchase_info)
			if not is_success:
				reasons.append(reason)
				self.release(resources)
				break
			elif resource:
				if isinstance(resource, list):
					resources.extend(resource)
				else:
					resources.append(resource)
			else:
				logging.error("`resource` SHOULD NOT be None! Please check it.")
		
		return is_success, reasons, resources

	def release(self, resources):
		if not resources:
			return 
		for allocator in self.context['allocators']:
			allocator.release(resources)
