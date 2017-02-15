# -*- coding: utf-8 -*-
"""@package business.mall.product_model
商品规格
"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from db.account import models as account_models
from db.mall import promotion_models
from eaglet.core import watchdog
from business import model as business_model
import settings
from business.mall.promotion.cps_promote_detail import CPSPromotionDetail


class ProductCustomizedPrice(business_model.Model):
	"""
	社群在固定低价合作模式下,会在加价基础上再修改售价
	"""
	__slots__ = (
		'id',
		'corp_id'
		'product_id',
		'product_model_id',
		'price',
		
	)

	def __init__(self, db_model=None,):
		business_model.Model.__init__(self)

		if db_model:
			self._init_slot_from_model(db_model)
	
	def from_product_info(self, product_id, product_model_id, webapp_owner):
		db_model = mall_models.ProductCustomizedPrice.select().dj_where(corp_id=webapp_owner.id,
																		product_id=product_id,
																		product_model_id=product_model_id).first()
		
		if db_model:
			return ProductCustomizedPrice(db_model)
		else:
			return None
