# -*- coding: utf-8 -*-
"""@package business.mall.review.review_product_factory.ReviewProductFactory
订单生成器

"""

import json
from bs4 import BeautifulSoup
import math
import itertools
import uuid
import time
import random
import string
from hashlib import md5
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils
from db.mall import models as mall_models
#import resource
from eaglet.core import watchdog
from business import model as business_model 
import settings
from business.decorator import cached_context_property

from business.mall.review.reviewed_product import ReviewedProduct
import logging

class ReviewProductFactory(business_model.Model):
	"""订单评论工厂类
	"""
	__slots__ = ()

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'order_id', 'product_id', 'order_review_id', 'review_detail', 'product_score', 'order_has_product_id', 'picture_list'])
	def create(args):
		"""工厂方法，创建ReviewProductFactory对象

		@return ReviewedProduct对象
		"""
		review_order_factory = ReviewProductFactory(
			args['webapp_owner'], 
			args['webapp_user'], 
			args['order_id'], 
			args['product_id'], 
			args['order_review_id'], 
			args['review_detail'], 
			args['product_score'], 
			args['order_has_product_id'], 
			args['picture_list'])

		return review_order_factory

	def __init__(self, webapp_owner, webapp_user, order_id, product_id, order_review_id, review_detail, product_score, order_has_product_id, picture_list):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user
		self.context['order_id'] = order_id
		self.context['product_id'] = product_id
		self.context['order_review_id'] = order_review_id
		self.context['review_detail'] = review_detail
		self.context['product_score'] = product_score
		self.context['order_has_product_id'] = order_has_product_id
		self.context['picture_list'] = picture_list

	def save(self):
		"""保存信息
		"""
		model, created = mall_models.ProductReview.get_or_create(
			member_id=self.context['webapp_user'].member.id,
			order_review=self.context['order_review_id'],
			order_id=self.context['order_id'],
			owner_id=self.context['webapp_owner'].id,
			product_id=self.context['product_id'],
			order_has_product=self.context['order_has_product_id'],
			product_score=self.context['product_score'],
			review_detail=self.context['review_detail']
		)
		product_review = ReviewedProduct.from_model({
			'webapp_owner':self.context['webapp_owner'],
			'model': model
			})
		logging.info("product_review={}".format(product_review.to_dict()))

		picture_list = self.context['picture_list']
		ReviewProductFactory.create_reviewed_product_pictures({
			'reviewed_id': model.id,
			'pictures': picture_list,
			'order_has_product_id': self.context['order_has_product_id']
			})
		# if picture_list:
		# 	logging.info("saving product review picture list..., picture_list=%s" % picture_list)
		# 	for picture in list(eval(picture_list)):
		# 		mall_models.ProductReviewPicture(
		# 			product_review=model,
		# 			order_has_product=self.context['order_has_product_id'],
		# 			att_url=picture
		# 		).save()

		return product_review

	@staticmethod
	@param_required(['reviewed_id', 'pictures', 'order_has_product_id'])
	def create_reviewed_product_pictures(args):
		reviewed_id = args['reviewed_id']
		pictures = args['pictures']
		order_has_product_id = args['order_has_product_id']
		if pictures:
			for picture in list(eval(pictures)):
				mall_models.ProductReviewPicture(
					product_review=reviewed_id,
					order_has_product=order_has_product_id,
					att_url=picture
				).save()
