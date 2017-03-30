# -*- coding: utf-8 -*-
"""@package business.mall.allocator.allocate_price_related_resource_service.AllocatePriceRelatedResourceService
订单资源分配器

"""

#import logging
from allocate_resource_service_base import AllocateResourceServiceBase
from business.wzcard.wzcard_resource_allocator import WZCardResourceAllocator
from business.member_card.member_card_resource_allocator import MemberCardResourceAllocator
from business.third_party_pay.jinge_card_resource_allocator import JinGeCardResourceAllocator

class AllocatePriceRelatedResourceService(AllocateResourceServiceBase):
	"""
	分配价格相关资源
	"""

	def __init__(self, webapp_owner, webapp_user):
		AllocateResourceServiceBase.__init__(self, webapp_owner, webapp_user)
		self.register_allocator(MemberCardResourceAllocator(webapp_owner, webapp_user))
		self.register_allocator(WZCardResourceAllocator(webapp_owner, webapp_user))
		self.register_allocator(JinGeCardResourceAllocator(webapp_owner, webapp_user))
