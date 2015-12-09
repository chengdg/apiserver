# -*- coding: utf-8 -*-
"""@package business.inegral_allocator.IntegralResourceAllocator
请求积分资源

"""
from db.mall import promotion_models

from business import model as business_model
from wapi.decorators import param_required


class CouponResource(business_model.Resource):
	"""积分资源
	"""
	__slots__ = (
		'type',
		'coupon',
		'money'
	)

	@staticmethod
	@param_required(['type'])
	def get(args):
		"""工厂方法，创建IntegralResource对象

		@return IntegralResource对象
		"""
		coupon_resource = CouponResource(args['type'])

		return coupon_resource

	def __init__(self, type):
		business_model.Resource.__init__(self)
		self.type = type

	def release(self):
		# todo 更新红包优惠券分析数据
		promotion_models.Coupon.update(status=self.context['raw_status'], member_id=self.context['raw_member_id']).where(
				promotion_models.Coupon.id == self.coupon.id).execute()
		if not self.context['raw_member_id']:
			promotion_models.CouponRule.update(remained_count=promotion_models.CouponRule.remained_count + 1)

		promotion_models.CouponRule.update(use_count=promotion_models.CouponRule.use_count - 1)

	def get_type(self):
		return self.type

	def use_coupon(self, coupon, coupon_rule, member_id):
		self.coupon = coupon
		self.money = coupon.money

		self.context['raw_status'] = coupon.status
		self.context['raw_member_id'] = coupon.member_id
		try:
			promotion_models.Coupon.update(status=promotion_models.COUPON_STATUS_USED, member_id=member_id).where(
				promotion_models.Coupon.id == coupon.id).execute()

			if not coupon.member_id:
				promotion_models.CouponRule.update(remained_count=promotion_models.CouponRule.remained_count - 1)

			promotion_models.CouponRule.update(use_count=promotion_models.CouponRule.use_count + 1)
		except BaseException as e:
			print e
			return False, u'使用优惠券失败'
		# todo 更新红包优惠券分析数据
		return True, ''
