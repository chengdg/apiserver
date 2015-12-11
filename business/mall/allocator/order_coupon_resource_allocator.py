# -*- coding: utf-8 -*-
"""@package business.inegral_allocator.OrderIntegralAllocator
请求积分资源

"""

from business import model as business_model
from business.mall.allocator.coupon_resource_allocator import CouponResourceAllocator
from business.mall.coupon.coupon import Coupon
from business.mall.coupon.coupon_rule import CouponRule
from business.resource.coupon_resource import CouponResource


class OrderCouponResourceAllocator(business_model.Model):
	"""下单使用优惠券（通用券）
	"""
	__slots__ = (
		'order',
		'result'
	)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

	def allocate_resource(self, order, purchase_info):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']
		member_id = webapp_user.member.id
		use_common_coupon = True

		if not purchase_info.coupon_id or purchase_info.coupon_id == '0':
			# 未使用优惠券
			self.__return_empty_coupon()
		else:
			coupon = Coupon.from_coupon_id({'coupon_id': purchase_info.coupon_id})
			if not coupon:
				reason = u'请输入正确的优惠券号'
				return False, reason, None
			else:
				coupon_rule = CouponRule.from_id({"id": coupon.coupon_rule.id})
				if coupon_rule.limit_product:
					use_common_coupon = False

			# 使用的优惠券非通用券
			if not use_common_coupon:
				self.__return_empty_coupon()

			# 判断通用券在订单中是否可用
			is_success, reason = coupon.check_common_coupon_in_order(order, purchase_info, member_id)
			if not is_success:
				return False, reason, None

			# 调用CouponResourceAllocator获得资源
			coupon_resource_allocator = CouponResourceAllocator(webapp_owner, webapp_user)
			is_success, reason, coupon_resource = coupon_resource_allocator.allocate_resource(coupon)

			if is_success:
				return True, '', coupon_resource
			else:
				return False, reason, None

	def release(self, resources):
		for resource in resources:
			if resource.get_type() == business_model.RESOURCE_TYPE_COUPON:
				CouponResourceAllocator.release(resource)

	def __return_empty_coupon(self):
		empty_coupon_resource = CouponResource.get({
			'type': business_model.RESOURCE_TYPE_COUPON,
		})
		empty_coupon_resource.coupon = None
		empty_coupon_resource.money = 0

		return True, '', empty_coupon_resource
	
	#add by bert
	def release(self,resources):
		pass
