# -*- coding: utf-8 -*-
"""@package business.mall.product
商品

Product是商品业务对象的实现，内部使用CachedProduct对象进行redis的读写操作。
OrderProduct，ShoppingCartProduct等更特定的商品业务对象都在内部使用Product业务对象实现。
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

	def get_product_catalogs(args):
		try:
			product_catalogs = mall_models.ProductCatalog.select()
			return product_catalogs
		except:
			watchdog.alert(unicode_full_stack())
			return False

