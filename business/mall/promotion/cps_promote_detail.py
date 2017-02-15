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
from db.mall import promotion_models
from eaglet.core import watchdog
from business import model as business_model
import settings


class CPSPromotionDetail(business_model.Model):
	"""
	商品 cps推广信息
	"""
	__slots__ = (
		'id',
		'promote_status',
		'promote_money',
		'promote_stock',
		'promote_time_from',
		'promote_time_to',
		'promote_sale_count',
		'promote_total_money'
		
	)

	def __init__(self, db_model=None):
		business_model.Model.__init__(self)

		if db_model:
			self._init_slot_from_model(db_model)
	
	def get_promoting_detail_by_product_id(self, product_id):
		db_model = mall_models.PromoteDetail.select().dj_where(product_id=product_id,
															   promote_status=mall_models.PROMOTING).first()
		if db_model:
			return CPSPromotionDetail(db_model)
		else:
			return None
	