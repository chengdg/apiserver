# -*- coding: utf-8 -*-
"""@package wapi.mall.a_coupons
优惠券列表资源

"""

import os
import copy
from datetime import datetime
import json

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from utils import dateutil as utils_dateutil
from business.mall.coupon.coupon import Coupon
from business.mall.reserved_product import ReservedProduct
from business.mall.forbidden_coupon_product_ids import ForbiddenCouponProductIds

class ACoupons(api_resource.ApiResource):
	"""
	优惠券列表
	"""
	app = 'mall'
	resource = 'coupons'

	@param_required(['woid'])
	def get(args):
		webapp_user = args['webapp_user']
		unused_coupons = []
		used_coupons = []
		expired_coupons = []
		for coupon in webapp_user.all_coupons:
			if coupon.is_can_use_by_webapp_user(webapp_user):
				unused_coupons.append(coupon.to_dict())
			elif coupon.is_expired():
				expired_coupons.append(coupon.to_dict())
			else:
				used_coupons.append(coupon.to_dict())

		return {
			'unused_coupons': unused_coupons,
			'used_coupons': used_coupons,
			'expired_coupons': expired_coupons
		}
