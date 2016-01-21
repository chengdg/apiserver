# -*- coding: utf-8 -*-
"""@package wapi.mall.a_coupon
优惠券接口 - 下订单时填写优惠码的教研

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


class ACoupon(api_resource.ApiResource):
	"""
	优惠券接口 - 下订单时填写优惠码的教研
	"""
	app = 'mall'
	resource = 'coupon'

	@param_required(['woid', 'coupon_id', 'order_price', 'product2info'])
	def get(args):
		"""
		优惠券接口 - 下订单时填写优惠码的教研
		@param coupon_id
		@param order_price
		@param product2info
		@return
			if can_use_coupon:
				return {
					'is_success': True,
					'id': coupon.coupon_id,
					'money': coupon.money,
					'productid': coupon.limit_product_id
				}
			else:
				return {
					'is_success': False,
					'msg': reason
				}

		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']

		coupon = Coupon.from_coupon_id({
			'coupon_id': args['coupon_id']
		})
		if coupon:
			forbidden_coupon_product_ids = ForbiddenCouponProductIds.get_for_webapp_owner({
				'webapp_owner': webapp_owner
			}).ids

			reserved_products = []
			product2info = json.loads(args['product2info'])
			for product_info in product2info:
				product_id = int(product_info['id'])
				reserved_product = ReservedProduct(webapp_owner, webapp_user)
				reserved_product.id = product_id
				reserved_product.price = product_info['price']
				reserved_product.original_price = product_info['original_price']
				reserved_product.purchase_count = product_info['count']
				if product_id in forbidden_coupon_product_ids:
					reserved_product.can_use_coupon = False
				else:
					reserved_product.can_use_coupon = True

				reserved_products.append(reserved_product)

			can_use_coupon, reason = coupon.is_can_use_for_products(webapp_user, reserved_products)
		else:
			# 输入的优惠卷号不存在时
			can_use_coupon = False
			reason = u'请输入正确的优惠券号'
		if can_use_coupon:
			return {
				'is_success': True,
				'id': coupon.coupon_id,
				'money': coupon.money,
				'productid': coupon.limit_product_id				
			}
		else:
			return {
				'is_success': False,
				'msg': reason
			}
