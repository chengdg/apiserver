# -*- coding: utf-8 -*-
"""@package business.product_catalog
商品分类信息
"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from core.exceptionutil import unicode_full_stack
from eaglet.decorator import param_required
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from eaglet.core import watchdog
from business import model as business_model



class ProductCatalog(business_model.Model):
	"""
	商品分类信息
	"""
	__slots__ = (
		'id',
		'name',
		'level',
		'father_id'
	)

	def __init__(self, model=None):
		business_model.Model.__init__(self)

	@staticmethod
	def get_product_catalogs():
		try:
			product_catalogs = mall_models.Classification.select()
			return product_catalogs
		except:
			watchdog.alert(unicode_full_stack())
			return False

	@staticmethod
	@param_required(['product_id'])
	def fill_product_catalog_id(args):
		product_catalog_id = mall_models.ClassificationHasProduct.select().dj_where(product_id=args['product_id']).first()
		if product_catalog_id:
			return True, product_catalog_id.classification_id
		else:
			return False, 0

