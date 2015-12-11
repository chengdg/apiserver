# -*- coding: utf-8 -*-
"""@package business.inegral_allocator.OrderIntegralAllocator
请求积分资源

"""

from business import model as business_model
from business.mall.coupon.coupon import Coupon
from business.mall.coupon.coupon_rule import CouponRule
from business.resource.coupon_resource import CouponResource


class OrderCouponResourceAllocator(business_model.Model):
	"""下单使用积分
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
		coupon_resource = CouponResource.get({
			'type': business_model.RESOURCE_TYPE_COUPON,
		})

		coupon_resource.coupon = None
		coupon_resource.money = 0

		use_common_coupon = True

		if not purchase_info.coupon_id or purchase_info.coupon_id == '0':
			# 未使用优惠券
			return True, '', coupon_resource
		else:
			coupon = Coupon.from_coupon_id({'coupon_id': purchase_info.coupon_id})
			if not coupon:
				reason = u'请输入正确的优惠券号'
				return False, reason, None
			else:
				coupon_rule = CouponRule.from_id({"id": coupon.coupon_rule.id})
				if coupon_rule.limit_product:
					use_common_coupon = False

		# 判断是否有通用券
		if not use_common_coupon:

			return True, '', coupon_resource

		is_success, reason = coupon.check_common_coupon_in_order(order, purchase_info, member_id)
		if not is_success:
			return False, reason, None

		is_success, reason = coupon_resource.use_coupon(coupon, coupon_rule, member_id)
		if is_success:
			return True, '', coupon_resource
		else:
			return False, reason, None

	@staticmethod
	def release(resources):
		pass
