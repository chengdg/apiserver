# -*- coding: utf-8 -*-

from business import model as business_model
from business.mall.allocator.coupon_resource_allocator import CouponResourceAllocator
from business.mall.coupon.coupon import Coupon
from business.resource.coupon_resource import CouponResource

import requests

from business.resource.group_buy_resource import GroupBuyResource


class OrderGroupBuyAllocator(business_model.Service):
	__slots__ = ()


	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

	def allocate_resource(self, order, purchase_info):
		# 检测purchase_info互斥
		pass

		# 申请资源
		params_data = {'pid',order.products[0].id}
		group_buy_product_info = requests.get('sadasd', params=params_data)





		empty_coupon_resource = GroupBuyResource.get({
			'type': self.resource_type,
		})


		return True, '', empty_coupon_resource




	def release(self, resource):
		if resource.get_type() == self.resource_type:
			# 通知团购服务
			pass

	@property
	def resource_type(self):
		return business_model.RESOURCE_TYPE_GROUP_BUY