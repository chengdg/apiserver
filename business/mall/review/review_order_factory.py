# -*- coding: utf-8 -*-
"""@package business.mall.review.review_order_factory.ReviewOrderFactory
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

from wapi.decorators import param_required
from wapi import wapi_utils
from db.mall import models as mall_models
#import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
import settings
from business.decorator import cached_context_property

from business.mall.review.reviewed_order import ReviewedOrder


class ReviewOrderFactory(business_model.Model):
	"""订单评论工厂类
	"""
	__slots__ = ()

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'order_id', 'serve_score', 'deliver_score', 'process_score'])
	def create(args):
		"""工厂方法，创建ReviewOrderFactory对象

		@return ReviewedProduct对象
		"""
		review_order_factory = ReviewOrderFactory(args['webapp_owner'], args['webapp_user'], args['order_id'], args['serve_score'], args['deliver_score'], args['process_score'])

		return review_order_factory

	def __init__(self, webapp_owner, webapp_user, order_id, serve_score, deliver_score, process_score):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user
		self.context['order_id'] = order_id
		self.context['serve_score'] = serve_score
		self.context['deliver_score'] = deliver_score
		self.context['process_score'] = process_score

	def save(self):
		"""保存信息
		"""
		order_review, created = mall_models.OrderReview.get_or_create(
			order_id=self.context['order_id'],
			owner_id=self.context['webapp_owner'].id,
			member_id=self.context['webapp_user'].member.id,
			serve_score=self.context['serve_score'],
			deliver_score=self.context['deliver_score'],
			process_score=self.context['process_score'])

		return ReviewedOrder.from_model({
			'model': order_review
			})