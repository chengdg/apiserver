# -*- coding: utf-8 -*-
"""@package business.mall.allocator.allocator_order_resource_service.AllocateOrderResourceService
订单资源分配器

"""

import logging
from business import model as business_model 


class AllocateResourceServiceBase(business_model.Service):
	"""
	分配资源的基类
	"""
	__slots__=(
		'__allocators',
		'__webapp_owner',
		'__webapp_user',
	)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.__webapp_owner = webapp_owner
		self.__webapp_user = webapp_user
		self.__allocators = []

	def register_allocator(self, allocator):
		self.__allocators.append(allocator)

	def allocate_resource_for(self, order, purchase_info):
		"""
		分配资源接口

		@return (is_success, reasons, resources)
		"""
		resources = []
		is_success = True
		reasons = []
		for allocator in self.__allocators:
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
		"""
		释放资源
		"""
		if not resources:
			return 
		for allocator in self.__allocators:
			allocator.release(resources)
