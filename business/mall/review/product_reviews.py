# -*- coding: utf-8 -*-
"""@package business.mall.review.ProductReviews
获取webapp user 会员评价商品列表

"""

import json
from bs4 import BeautifulSoup
import math
import itertools

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.review.reviewed_product import ReviewedProduct
import settings


class ProductReviews(business_model.Model):
	"""商品评价信息
	"""
	__slots__ = (
		'products',
	)

	@staticmethod
	@param_required(['webapp_owner', 'product_id'])
	def get_from_product_id(args):
		"""工厂方法，根据webapp_user创建ReviewedProducts对象对象

		@param[in] webapp_owner: webapp_owner
		@param[in] product_id: product_id

		@return ProductReviews
		"""
		product_reviews = ProductReviews(args['webapp_owner'], args['product_id'])
		return product_reviews

	def __init__(self, webapp_owner, product_id):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['product_id'] = product_id
		self.__get_product_reviews_for(product_id)

	def __get_product_reviews_for(self, product_id):
		webapp_owner = self.context['webapp_owner']
		reviewed_products = mall_models.ProductReview.select().dj_where(
			owner_id=webapp_owner.id, 
			product_id=product_id,
			status__in=[
				mall_models.PRODUCT_REVIEW_STATUS_PASSED,
				mall_models.PRODUCT_REVIEW_STATUS_PASSED_PINNED
				]).order_by(-mall_models.ProductReview.top_time, -mall_models.ProductReview.id)

		products = []
		for reviewed_product in reviewed_products:
			products.append(ReviewedProduct.from_model({
				"webapp_owner": webapp_owner,
				"model": reviewed_product
				}).to_dict())

		self.products = products


