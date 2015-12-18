# -*- coding: utf-8 -*-
"""@package wapi.mall.a_coupon
优惠券接口

"""
import os
import copy
from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from utils import dateutil as utils_dateutil
from business.mall.coupon.coupon import Coupon


class ACoupon(api_resource.ApiResource):
	"""
	优惠券
	"""
	app = 'mall'
	resource = 'coupon'

	@param_required(['woid', 'coupon_id', 'order_price', 'product2info'])
	def get(args):
		coupon = Coupon.from_coupon_id({
			'coupon_id': args['coupon_id']
		})

		if not coupon:
			return {
				'is_success': False,
				'msg': u'请输入正确的优惠券号'
			}

		if not coupon.is_can_use_by_webapp_user(args['webapp_user']):
			return {
				'is_success': False,
				'msg': coupon.invalid_reason
			}

		if coupon.is_specific_product_coupon():
			return {
				'is_success': True
			}
		else:
			if coupon.valid_restrictions > float(args['order_price']):
				return {
					'is_success': False,
					'type': 'not_match_valid_restrictions',
					'msg': u'该优惠券不满足使用金额限制',
				}
			else:				
				return {
					'is_success': True,
					'id': coupon.id,
					'money': coupon.money,
					'productid': coupon.limit_product_id
				}
