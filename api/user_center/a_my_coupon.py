# -*- coding: utf-8 -*-
"""
个人中心-我的优惠券接口
"""
from eaglet.core import api_resource
from eaglet.decorator import param_required
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
			#个人中心的优惠券列表加入使用说明的展示 duhao 20161206
			data = c.to_dict()
			data['remark'] = c.coupon_rule.remark

			if c.status == promotion_models.COUPON_STATUS_USED:
				used_coupons.append(data)

			if c.status == promotion_models.COUPON_STATUS_UNUSED:
				unused_coupons.append(data)

			if c.status == promotion_models.COUPON_STATUS_EXPIRED:
				expired_coupons.append(data)

		return {
			'used_coupons': used_coupons,
			'unused_coupons': unused_coupons,
			'expired_coupons': expired_coupons,
		}


