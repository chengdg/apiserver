# -*- coding: utf-8 -*-
"""@package business.mall.allocator.allocator_order_resource_service.AllocateOrderResourceService
订单资源分配器（分配价格无关资源）

"""

#from business import model as business_model 

from allocate_resource_service_base import AllocateResourceServiceBase

from business.mall.allocator.order_integral_resource_allocator import OrderIntegralResourceAllocator
from business.mall.allocator.order_products_resource_allocator import OrderProductsResourceAllocator
from business.mall.allocator.order_coupon_resource_allocator import OrderCouponResourceAllocator

import logging


class AllocateOrderResourceService(AllocateResourceServiceBase):
	"""
	分配价格无关资源
	"""

	def __init__(self, webapp_owner, webapp_user):
		"""
		**注意**：这里的顺序非常重要！
		
		`OrderProductsResourceAllocator` 必须要在 `OrderIntegralResourceAlloctor` 之前，
		因为买赠会修改积分应用计算积分金额限额的价格基数（当有买赠时，按原价计算；当没有买赠时，按会员价计算）
		"""

		AllocateResourceServiceBase.__init__(self, webapp_owner, webapp_user)

		# 顺序非常重要！
		self.register_allocator(OrderProductsResourceAllocator(webapp_owner, webapp_user))
		self.register_allocator(OrderIntegralResourceAllocator(webapp_owner, webapp_user))
		self.register_allocator(OrderCouponResourceAllocator(webapp_owner, webapp_user))


	def allocate_resources(self, order, extracted_resources):
		"""
		分配抽取的资源

		@return (is_success, reasons, resources)
		"""
		resources = []
		is_success = True
		reasons = []
		webapp_owner = self.__webapp_owner
		webapp_user = self.__webapp_user

		# TODO: to be replaced with self.__allocators
		__allocators = [
			OrderProductsResourceAllocator(webapp_owner, webapp_user),
			OrderIntegralResourceAllocator(webapp_owner, webapp_user),
		]
		for allocator in __allocators:
			logging.info("allocating resource using {}".format(allocator))
			is_success, reason, allocated_resources = allocator.allocate_resource(order, extracted_resources)
			resources.extend(allocated_resources)
			logging.info("allocation result: is_success: {}, reason: {}, resource: {}".format(is_success, reason, allocated_resources))
			if not is_success:
				if resource:
					resources.append(resource)
				reasons.append(reason)
				self.release(resources)
				resources = []
				break
			elif resource:
				if isinstance(resource, list):
					resources.extend(resource)
				else:
					resources.append(resource)
			else:
				logging.error("`resource` SHOULD NOT be None! Please check it.")
		
		# 如果失败，resources为[]
		return is_success, reasons, resources

'''
class AllocateOrderResourceService0(business_model.Service):

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
'''