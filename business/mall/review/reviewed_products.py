# -*- coding: utf-8 -*-
"""@package business.mall.review.ReviewedProducts
获取webapp user 评价商品列表

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


class ReviewedProducts(business_model.Model):
	"""评论商品集合
	"""
	__slots__ = (
		'products',
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def get_for_webapp_user(args):
		"""工厂方法，根据Order创建OrderProducts对象

		@param[in] order: 购买信息PurchaseInfo对象

		@return OrderProducts对象
		"""
		reviewed_products = ReviewedProducts(args['webapp_owner'], args['webapp_user'])
		#order_products.__get_products_for_order(args['order'])
		return reviewed_products

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		self.__get_reviewed_products_for()

	def __get_reviewed_products_for(self):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']
		reviewed_products = mall_models.ProductReview.select().dj_where(member_id=webapp_user.member.id).order_by(-mall_models.ProductReview.id)

		products = []
		for reviewed_product in reviewed_products:
			products.append(ReviewedProduct.from_model({
				"webapp_owner": webapp_owner,
				"model": reviewed_product
				}).to_dict())

		self.products = products

