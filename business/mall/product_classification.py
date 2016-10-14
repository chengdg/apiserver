# -*- coding: utf-8 -*-
"""@package business.product_classification
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



class ProductClassification(business_model.Model):
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
	def get_product_classifications():
		try:
			product_classifications = mall_models.Classification.select().dj_where(status=1)
			product_classifications = [ProductClassification(classification) for classification in product_classifications]
			return product_classifications
		except:
			watchdog.alert(unicode_full_stack())
			return False

