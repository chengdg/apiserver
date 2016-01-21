# -*- coding: utf-8 -*-
"""
个人中心-我的优惠券接口
"""
from core import api_resource
from wapi.decorators import param_required
from db.mall import promotion_models


class AMyCoupon(api_resource.ApiResource):
	"""
	个人中心-我的优惠券
	"""
	app = 'user_center'
	resource = 'my_coupon'

	@param_required([])
	def get(args):
		"""
		获取个人中心-我的优惠券
		@param 无
		@return {
			'used_coupons': used_coupons,
			'unused_coupons': unused_coupons,
			'expired_coupons': expired_coupons,
		}
		"""
		webapp_user = args['webapp_user']
		coupons = webapp_user.coupons
		used_coupons = []
		unused_coupons = []
		expired_coupons = []

		for c in coupons:
			if c.status == promotion_models.COUPON_STATUS_USED:
				used_coupons.append(c.to_dict())

			if c.status == promotion_models.COUPON_STATUS_UNUSED:
				unused_coupons.append(c.to_dict())

			if c.status == promotion_models.COUPON_STATUS_EXPIRED:
				expired_coupons.append(c.to_dict())

		return {
			'used_coupons': used_coupons,
			'unused_coupons': unused_coupons,
			'expired_coupons': expired_coupons,
		}


