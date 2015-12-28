# -*- coding: utf-8 -*-
"""@package business.mall.review.waiting_review_orders.WaitingReviewOrder
获取webapp user 待评论订单对象

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
from business.mall.order import Order
from business.mall.order_products import OrderProducts
import settings
import logging


class WaitingReviewOrder(business_model.Model):
	"""待评论订单对象
	"""
	__slots__ = (
		'id',
		'order_id',
		'products',
		'order_is_reviewed',
		'created_at',
		'final_price',
		'reviewed'
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'order'])
	def get_for_order(args):
		"""工厂方法，根据order_id创建WaitingReviewOrder对象

		@param[in] order: order

		@return OrderProducts对象
		"""
		waiting_review_orders = WaitingReviewOrder(args['webapp_owner'],args['webapp_user'],args['order'])
		return waiting_review_orders

	def __init__(self, webapp_owner, webapp_user, order):
		business_model.Model.__init__(self)

		self.context['order'] = order
		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user


		self.__get_waiting_review_order()

	def __get_waiting_review_order(self):
		order = self.context['order'] 
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		order_products = OrderProducts.get_for_order({
				'webapp_owner': webapp_owner,
				'webapp_user': webapp_user,
				'order': order
			})

		reviewed = False
		order_is_reviewed = True
		products = order_products.products

		products_list = []
		for order_product in products:
			if order_product.promotion:
				if order_product.promotion['type_name'] == 'premium_sale:premium_product':
					continue
			
			has_reviewed_picture = False
			has_reviewed = False
			
			rid = order_product.rid
			for product_review in mall_models.ProductReview.select().dj_where(product_id=order_product.id, order_has_product_id=rid, order_id=order.id, member_id=webapp_user.member.id):
				reviewed = True
				has_reviewed = True
				if mall_models.ProductReviewPicture.select().dj_where(product_review=product_review).count() > 0:
					has_reviewed_picture = True
					break

			order_product.has_reviewed_picture = has_reviewed_picture
			order_product.has_reviewed = has_reviewed

			if not order_product.has_reviewed and order_is_reviewed:
				order_is_reviewed = False
			
			if not order_product.has_reviewed_picture:
				order_is_reviewed = False

			products_list.append(order_product)

		self.products = products_list
		self.order_is_reviewed = order_is_reviewed
		self.order_id = order.order_id
		self.created_at = order.created_at
		self.id = order.id
		self.final_price = order.final_price
		self.reviewed = reviewed