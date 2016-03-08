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

		if not order.group_id:
			self.__return_empty_resource()

		# 检测purchase_info互斥
		pass

		group_buy_product_id = order.products[0].id

		# 检测活动可行性

		# 申请资源
		params_data = {'pid',order.products[0].id}
		# group_buy_product_info = requests.get('sadasd', params=params_data)

		mock_group_buy_product_info = {
			'is_success': True,
			'group_buy_price': 123,
			'reason': 'asdasdasdasda',
		}



		group_buy_product_info = mock_group_buy_product_info

		if not group_buy_product_info['is_success']:
			# 申请资源失败
			reason_dict = {
				"is_success": False,
				"msg": group_buy_product_info['reason'],
				"type": "group_buy"
			}
			return False, [reason_dict], None



		group_buy_resource = GroupBuyResource.get({
			'type': self.resource_type,
		})

		group_buy_resource.pid = group_buy_product_id
		group_buy_resource.group_buy_price = group_buy_product_info['group_buy_price']

		return True, '', group_buy_resource




	def release(self, resource):
		if resource.get_type() == self.resource_type:
			# 通知团购服务
			pass

	@property
	def resource_type(self):
		return business_model.RESOURCE_TYPE_GROUP_BUY

	def __return_empty_resource(self):
		empty_coupon_resource = GroupBuyResource.get({
			'type': self.resource_type,
		})
		return True, '',empty_coupon_resource
