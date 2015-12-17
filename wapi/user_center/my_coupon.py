# -*- coding: utf-8 -*-

from business.mall.coupon.coupon import Coupon
from core import api_resource
from wapi.decorators import param_required
from db.mall import promotion_models


class AMyCoupon(api_resource.ApiResource):
	"""
	个人中心
	"""
	app = 'user_center'
	resource = 'my_coupon'

	@param_required([])
	def get(args):
		"""
		获取个人中心
		"""
		webapp_user = args['webapp_user']
		coupons = Coupon.get_coupons_by_webapp_user({'webapp_user': webapp_user})
		used_coupons = []
		unused_coupons = []
		expired_coupons = []

		for c in coupons:
			c.consumer_name = ''
			if c.status == promotion_models.COUPON_STATUS_USED:
				used_coupons.append(c)

			if c.status == promotion_models.COUPON_STATUS_UNUSED:
				unused_coupons.append(c)

			if c.status == promotion_models.COUPON_STATUS_EXPIRED:
				expired_coupons.append(c)

		return {
			'used_coupons': used_coupons,
			'unused_coupons': unused_coupons,
			'expired_coupons': expired_coupons,
		}


