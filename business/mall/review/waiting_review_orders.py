# -*- coding: utf-8 -*-
"""@package business.mall.review.waiting_review_orders.WaitingReviewOrders
获取webapp user 待评论订单集合

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
from business.mall.review.waiting_review_order import WaitingReviewOrder
from business.mall.order import Order
import settings


class WaitingReviewOrders(business_model.Model):
	"""待评论订单集合
	"""
	__slots__ = (
		'orders',
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def get_for_webapp_user(args):
		"""工厂方法，根据webapp_user创建WaitingReviewOrders对象

		@param[in] webapp_owner: webapp_owner
		@param[in] webapp_user: webapp_user

		@return OrderProducts对象
		"""
		waiting_review_orders = WaitingReviewOrders(args['webapp_owner'], args['webapp_user'])
		return waiting_review_orders

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		self.__get_waiting_review_orders()

	def __get_waiting_review_orders(self):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		orders = Order.get_finished_orders_for_webapp_user({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user
			})
		waiting_review_orders = []
		
		for order in orders:
			waiting_review_order = WaitingReviewOrder.get_for_order({
				'webapp_owner': webapp_owner,
				'order': order,
				'webapp_user': webapp_user
				})
			if waiting_review_order:
				waiting_review_orders.append(waiting_review_order)
		self.orders = waiting_review_orders
	