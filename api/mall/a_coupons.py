# -*- coding: utf-8 -*-
"""@package apimall.a_coupons
编辑订单页显示优惠券列表

"""

import os
import copy
from datetime import datetime
import json

from eaglet.core import api_resource
from eaglet.decorator import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from util import dateutil as utils_dateutil
from business.mall.coupon.coupon import Coupon
from business.mall.reserved_product import ReservedProduct
from business.mall.forbidden_coupon_product_ids import ForbiddenCouponProductIds

class ACoupons(api_resource.ApiResource):
	"""
	编辑订单页显示优惠券列表
	"""
	app = 'mall'
	resource = 'coupons'

	@param_required(['woid'])
	def get(args):
		"""
		编辑订单页显示优惠券列表
		@param 无
		@return
			return {
				'unused_coupons': unused_coupons,
				'used_coupons': used_coupons,
				'expired_coupons': expired_coupons
			}

		"""
		webapp_user = args['webapp_user']
		unused_coupons = []
		used_coupons = []
		expired_coupons = []
		for coupon in webapp_user.all_coupons:
			if coupon.is_can_use_by_webapp_user(webapp_user):
				unused_coupons.append(coupon.to_dict('coupon_rule_id'))
			elif coupon.is_expired():
				expired_coupons.append(coupon.to_dict('coupon_rule_id'))
			else:
				used_coupons.append(coupon.to_dict('coupon_rule_id'))

		return {
			'unused_coupons': unused_coupons,
			'used_coupons': used_coupons,
			'expired_coupons': expired_coupons
		}
