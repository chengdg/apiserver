# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup

from core import inner_resource
from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
import settings
import resource
from core.watchdog.utils import watchdog_alert


class RForbiddenCouponProductIds(inner_resource.Resource):
	"""
	商品详情
	"""
	app = 'mall'
	resource = 'forbidden_coupon_product_ids'

	@staticmethod
	def get_forbidden_coupon_product_ids_for_cache(webapp_owner_id):
		"""
		webapp_cache:get_forbidden_coupon_product_ids_for_cache
		"""
		def inner_func():
			forbidden_coupon_products = list(promotion_models.ForbiddenCouponProduct.select().dj_where(
				owner_id=webapp_owner_id, 
				status__in=(promotion_models.FORBIDDEN_STATUS_NOT_START, promotion_models.FORBIDDEN_STATUS_STARTED)
			))

			return {
					'keys': [
						'forbidden_coupon_products_%s' % (webapp_owner_id)
					],
					'value': forbidden_coupon_products
				}
		return inner_func

	@staticmethod
	def get_forbidden_coupon_product_ids(webapp_owner_id):
		"""
		webapp_cache:get_forbidden_coupon_product_ids
		获取商家的禁用全场优惠券的商品id列表 duhao
		"""
		key = 'forbidden_coupon_products_%s' % (webapp_owner_id)

		forbidden_coupon_products = cache_util.get_from_cache(key, RForbiddenCouponProductIds.get_forbidden_coupon_product_ids_for_cache(webapp_owner_id))
		product_ids = []
		for product in forbidden_coupon_products:
			if product.is_active:
				product_ids.append(product.product_id)
		return product_ids

	@param_required(['woid'])
	def get(args):
		webapp_owner_id = args['woid']
		return RForbiddenCouponProductIds.get_forbidden_coupon_product_ids(webapp_owner_id)



