# -*- coding: utf-8 -*-
"""@package business.mall.review.reviewed_product.ReviewedProduct
	商品评价对象ReviewedProduct
"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils

from db.mall import models as mall_models

#import resource
import settings
from core.watchdog.utils import watchdog_alert
from core.cache import utils as cache_util
from utils import emojicons_util

from business import model as business_model
from business.mall.review.reviewed_product_picture import ReviewedProductPicture
from business.mall.product import Product


class ReviewedProduct(business_model.Model):
	"""
	商品评价对象ReviewedProduct
	"""
	__slots__ = (
		'id',
		'member_id',
		'owner_id',
		'review_detail',
		'member_id',
		'status',
		'created_at',
		'reviewed_product_pictures',
		'product',
		'product_score'
	)

	@staticmethod
	@param_required(['webapp_owner', 'model'])
	def from_model(args): 
		"""
		工厂对象，根据ProductReview model获取ReviewedProduct业务对象

		@param[in] model: ReviewedProduct model

		@return ReviewedProduct业务对象
		"""
		model = args['model']
		webapp_owner = args['webapp_owner']

		reviewed_product = ReviewedProduct(webapp_owner, model)
		reviewed_product._init_slot_from_model(model)
		return reviewed_product

	@staticmethod
	@param_required(['id', 'webapp_owner'])
	def from_id(args):
		"""
		工厂对象，根据id获取ReviewedProduct业务对象

		@param[in] id: 会员的id

		@return ReviewedProduct业务对象
		"""
		id = args['id']
		webapp_owner = args['webapp_owner']
		try:
			db_model = mall_models.ProductReview.get(id=id)
			return ReviewedProduct.from_model({
				'webapp_owner': webapp_owner,
				'model': db_model
			})
		except:
			return None

	@staticmethod
	@param_required(['reviewed_order_id', 'product_id'])
	def from_product_id(args):
		"""
		工厂对象，根据id获取ReviewedProduct业务对象

		@param[in] reviewed_order_id: 订单评价id
		@param[in] product_id: 商品id

		@return ReviewedProduct业务对象
		"""
		product_id = args['product_id']
		reviewed_order_id = args['reviewed_order_id']
		try:
			db_model = mall_models.ProductReview.get(order_review_id=reviewed_order_id, product_id=product_id)
			return ReviewedProduct.from_model({
				'webapp_owner': webapp_owner,
				'model': db_model
			})
		except:
			return None

	@staticmethod
	@param_required(['webapp_owner', 'order_has_product_id'])
	def from_order_has_product_id(args):
		"""
		工厂对象，根据id获取ReviewedProduct业务对象

		@param[in] webapp_owner: webapp_owner
		@param[in] order_has_product_id: 订单商品r-id

		@return ReviewedProduct业务对象
		"""
		webapp_owner = args['webapp_owner']
		order_has_product_id = args['order_has_product_id']
		try:
			db_model = mall_models.ProductReview.get(order_has_product=order_has_product_id)
			return ReviewedProduct.from_model({
				'webapp_owner': webapp_owner,
				'model': db_model
			})
		except:
			return None

	def __init__(self, webapp_owner, model):
		business_model.Model.__init__(self)
		self.context['db_model'] = model
		self.context['webapp_owner'] = webapp_owner

		self.product_score = model.product_score

		self._get_reviewed_product_pictures()
		self.__fill_product_info()
		

	def _get_reviewed_product_pictures(self):
		model = self.context['db_model'] 
		reviewed_product_pictures = []
		for reviewed_product_picture in mall_models.ProductReviewPicture.select().dj_where(product_review=model):
			reviewed_product_pictures.append(ReviewedProductPicture.from_model({
				'model': reviewed_product_picture
				}).to_dict())

		self.reviewed_product_pictures = reviewed_product_pictures

	def __fill_product_info(self):
		model = self.context['db_model'] 
		webapp_owner = self.context['webapp_owner']
		product_mode = model.order_has_product.product
		product = Product.from_model({
			'webapp_owner': webapp_owner,
			'model': product_mode,
			'fill_options': {}

			})
		self.product = product.to_dict()


