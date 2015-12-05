# -*- coding: utf-8 -*-
"""@package business.mall.promotion.integral_sale_rule
积分应用规则，在积分应用中，我们可以为每个等级的会员设定一个积分应用规则

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
from core.watchdog.utils import watchdog_alert
from business import model as business_model
import settings
from business.mall.promotion import promotion


class IntegralSaleRule(business_model.Model):
	"""
	积分应用
	"""
	__slots__ = (
		'id',
		'member_grade_id',
		'discount',
		'discount_money'
	)

	def __init__(self, db_model=None):
		business_model.Model.__init__(self)

		self._init_slot_from_model(db_model)