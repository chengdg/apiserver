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
		'__type2allocator'
	)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.__webapp_owner = webapp_owner
		self.__webapp_user = webapp_user
		self.__allocators = []
		self.__type2allocator = {}

	def register_allocator(self, allocator):
		self.__allocators.append(allocator)
		self.__type2allocator[allocator.resource_type] = allocator
		logging.info("registered allocator: {} => {}".format(allocator.resource_type, allocator))

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
			is_success_once, failure_reasons, resource = allocator.allocate_resource(order, purchase_info)
			logging.info("allocation result: is_success: {}, reasons: {}, resource: {}".format(is_success, failure_reasons, resource))
			if not is_success_once:
				is_success = False
				if resource:
					resources.append(resource)
				reasons.extend(failure_reasons)
				#self.release(resources)
				#resources = []
				#break
			elif resource:
				if isinstance(resource, list):
					resources.extend(resource)
				else:
					resources.append(resource)
			else:
				logging.error("`resource` SHOULD NOT be None! Please check it.")
		if not is_success:
			# 释放已分配的资源
			logging.info("release all allocated resources: {}".format(resources))
			self.release(resources)
			resources = []
		
		# 如果失败，resources为[]
		return is_success, reasons, resources


	def _find_allocator_by_type(self, resource_type):
		return self.__type2allocator.get(resource_type)

	def release(self, resources):
		"""
		释放资源
		"""
		logging.info("trying to release resources in {}".format(self))
		if not resources:
			return
		for resource in resources:
			if resource:
				allocator = self._find_allocator_by_type(resource.type)
				if allocator:
					allocator.release(resource)
					logging.info("Resorce {} released".format(resource))
				else:
					logging.warning("No allocator of resource type '{}', resource: {}".format(resource.type, resource))
			else:
				logging.error("Unexpected None resource, skipped")
		#for allocator in self.__allocators:
		#	allocator.release(resources)
