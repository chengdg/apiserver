# -*- coding: utf-8 -*-
"""@package business.coupon_allocator.CouponResourceAllocator
请求积分资源

"""

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
		"""工厂方法，创建CouponResource对象

		@return CouponResource对象
		"""
		coupon_resource = CouponResource(args['type'])

		return coupon_resource

	def __init__(self, type):
		business_model.Resource.__init__(self)
		self.type = type

	def get_type(self):
		return self.type
