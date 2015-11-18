# -*- coding: utf-8 -*-

"""订单

"""

import json
from bs4 import BeautifulSoup
import math
import itertools
import uuid
import time
import random

from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.mall.order_products import OrderProducts
from business.mall.product_grouper import ProductGrouper
from business.mall.order_checker import OrderChecker


class Order(business_model.Model):
	"""订单生成器
	"""
	__slots__ = (
		'id',
		'order_id',
		'pay_interface_type',
		'final_price',
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'order_id'])
	def from_id(args):
		"""工厂方法，创建Order对象

		@return Order对象
		"""
		order = Order(args['webapp_owner'], args['webapp_user'], args['order_id'])
		return order

	@staticmethod
	def empty_order():
		"""工厂方法，创建空的Order对象

		@return Order对象
		"""
		order = Order(None, None, None)
		return order

	def __init__(self, webapp_owner, webapp_user, order_id):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		if order_id:
			order_db_model = mall_models.Order.get(order_id=order_id)
			self._init_slot_from_model(order_db_model)
