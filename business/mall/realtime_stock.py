# -*- coding: utf-8 -*-
"""实时库存信息

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model
import settings


class RealtimeStock(business_model.Model):
	"""
	实时库存信息
	"""
	__slots__ = (
		'model2stock',
	)

	@staticmethod
	@param_required(['product_id'])
	def from_product_id(args):
		"""
		工厂方法，根据product_id获取商品的实时库存信息

		@param[in] product_id: 商品id

		@return RealtimeStock业务对象
		"""
		product_id = args['product_id']
		models = mall_models.ProductModel.select().dj_where(product=product_id, is_deleted=False)
		realtime_stock = RealtimeStock()
		realtime_stock.init(models)

		return realtime_stock

	@staticmethod
	@param_required(['model_ids'])
	def from_product_model_ids(args):
		"""
		工厂方法，根据product_id获取相应的库存信息

		@param[in] product_id: 商品id

		@return RealtimeStock业务对象
		"""
		model_ids = args['model_ids']
		models = mall_models.ProductModel.select().dj_where(id__in=model_ids, is_deleted=False)
		realtime_stock = RealtimeStock()
		realtime_stock.init(models)

		return realtime_stock

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



