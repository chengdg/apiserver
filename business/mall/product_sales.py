# -*- coding: utf-8 -*-
"""@package business.mall.product_model
商品销量
"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from eaglet.core import watchdog
from business import model as business_model
import settings


class ProductSales(business_model.Model):
	"""
	商品销量
	"""
	__slots__ = (
		'id',
		'product_id',
		'sales'
	)

	def __init__(self, db_model=None):
		business_model.Model.__init__(self)

		if db_model:
			self._init_slot_from_model(db_model)

	def get_product_sales_by_ids(self, product_ids):
		db_models = mall_models.ProductSales.select().dj_where(product_id__in=product_ids)
		return [ProductSales(model) for model in db_models]
		