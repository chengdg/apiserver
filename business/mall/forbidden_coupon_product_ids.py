# -*- coding: utf-8 -*-
"""@package business.mall.forbidden_coupon_product_ids
禁用优惠券的商品id集合
"""

import json
from bs4 import BeautifulSoup
import math
import itertools

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from wapi.mall import models as mall_models
from wapi.mall import promotion_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
import settings


class ForbiddenCouponProductIds(business_model.Model):
	"""
	携带基础商品信息的商品集合
	"""
	__slots__ = (
		'ids',
	)

	@staticmethod
	@param_required(['webapp_owner'])
	def get_for_webapp_owner(args):
		"""
		factory方法
		"""
		webapp_owner = args['webapp_owner']
		
		ids = ForbiddenCouponProductIds(webapp_owner)
		return ids

	def __init__(self, webapp_owner):
		business_model.Model.__init__(self)

		self.ids = self.__get_forbidden_coupon_product_ids(webapp_owner.id)

	def __get_forbidden_coupon_product_ids_for_cache(self, webapp_owner_id):
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

	def __get_forbidden_coupon_product_ids(self, webapp_owner_id):
		"""
		webapp_cache:get_forbidden_coupon_product_ids
		获取商家的禁用全场优惠券的商品id列表 duhao
		"""
		key = 'forbidden_coupon_products_%s' % (webapp_owner_id)

		forbidden_coupon_products = cache_util.get_from_cache(key, self.__get_forbidden_coupon_product_ids_for_cache(webapp_owner_id))
		product_ids = set()
		for product in forbidden_coupon_products:
			if product.is_active:
				product_ids.add(product.product_id)

		return product_ids
