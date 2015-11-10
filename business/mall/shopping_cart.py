# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
from wapi.mall import promotion_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model
import settings


class ShoppingCart(business_model.Model):
	__slots__ = ['items', 'webapp_user']

	@staticmethod
	@param_required(['webapp_user'])
	def get_for_webapp_user(args):
		shopping_cart = ShoppingCart(webapp_user)

		return shopping_cart

	def __init__(self, webapp_user=None):
		business_model.Model.__init__(self)

		self.webapp_user = webapp_user

	def add_product(product_id, product_model_name, count):
		try:
			shopping_cart_item = mall_models.ShoppingCart.get(
				mall_models.ShoppingCart.webapp_user_id == self.webapp_user.id,
				mall_models.ShoppingCart.product == product_id,
				mall_models.ShoppingCart.product_model_name == product_model_name
			)
			shopping_cart_item.count = shopping_cart_item.count + count
			shopping_cart_item.save()
		except:
			mall_models.ShoppingCart.create(
				webapp_user_id = self.webapp_user.id,
				product = product_id,
				product_model_name = product_model_name,
				count = count
			)

	@property
	def product_count(self):
		"""
		获得购物车中商品数量
		"""
		return mall_models.ShoppingCart.select().dj_where(webapp_user_id=self.webapp_user.id).count()
