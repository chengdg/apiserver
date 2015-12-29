# -*- coding: utf-8 -*-
"""@package business.inegral_allocator.OrderIntegralAllocator
请求积分资源

"""

from business import model as business_model
from business.mall.allocator.coupon_resource_allocator import CouponResourceAllocator
from business.mall.coupon.coupon import Coupon
from business.resource.coupon_resource import CouponResource


class OrderCouponResourceAllocator(business_model.Model):
	"""下单使用优惠券
	"""
	__slots__ = (
	)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

	def allocate_resource(self, order, purchase_info):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		is_success = True
		reason = ''
		coupon_resource = None

		if not purchase_info.coupon_id or purchase_info.coupon_id == '0':
			# 未使用优惠券
			self.__return_empty_coupon()
		else:
			coupon = Coupon.from_coupon_id({'coupon_id': purchase_info.coupon_id})
			if not coupon:
				reason = u'请输入正确的优惠券号'
				is_success = False
			else:
				# 判断优惠券在订单中是否可用
				is_success, reason = coupon.check_coupon_in_order(order, webapp_user)
				if is_success:
					# 调用CouponResourceAllocator获得资源
					coupon_resource_allocator = CouponResourceAllocator(webapp_owner, webapp_user)
					is_success, reason, coupon_resource = coupon_resource_allocator.allocate_resource(coupon)

		if is_success:
			return True, [{}], coupon_resource
		else:
			reason_dict = {
				"is_success": False,
				"msg": reason,
				"type": "coupon"
			}
			return False, [reason_dict], None


	def release(self, resources):
		for resource in resources:
			if resource.get_type() == business_model.RESOURCE_TYPE_COUPON:
				CouponResourceAllocator.release(resource)

	def __return_empty_coupon(self):
		empty_coupon_resource = CouponResource.get({
			'type': self.resource_type,
		})
		empty_coupon_resource.coupon = None
		empty_coupon_resource.money = 0

		return True, '', empty_coupon_resource

	@property
	def resource_type(self):
		return business_model.RESOURCE_TYPE_COUPON
