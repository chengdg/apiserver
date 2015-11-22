# -*- coding: utf-8 -*-
"""@package business.mall.product_stocks
商品库存?

"""

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


class ProductStocks(business_model.Model):
	"""
	商品
	"""
	__slots__ = (
		'model2stock',
	)

	@staticmethod
	@param_required(['product_id'])
	def from_product_id(args):
		product_id = args['product_id']
		models = mall_models.ProductModel.select().dj_where(product=product_id, is_deleted=False)
		product_stocks = ProductStocks()
		product_stocks.init(models)

		return product_stocks

	@staticmethod
	@param_required(['model_ids'])
	def from_product_model_ids(args):
		model_ids = args['model_ids']
		models = mall_models.ProductModel.select().dj_where(id__in=model_ids, is_deleted=False)
		product_stocks = ProductStocks()
		product_stocks.init(models)

		return product_stocks

	def __init__(self):
		business_model.Model.__init__(self)

	def init(self, models):
		self.model2stock = dict()
		for model in models:
			model_data = dict()
			model_data["stocks"] = model.stocks
			model_data["stock_type"] = model.stock_type
			self.model2stock[model.id] = model_data

	def to_dict(self, **kwargs):
		return self.model2stock
