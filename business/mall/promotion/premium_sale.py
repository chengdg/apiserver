# -*- coding: utf-8 -*-
"""@package business.mall.promotion.premium_sale
买赠

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


class PremiumSale(promotion.Promotion):
	"""
	限时抢购
	"""
	__slots__ = (
		'count',
		'is_enable_cycle_mode',
		'premium_products'
	)

	def __init__(self, promotion_model=None):
		promotion.Promotion.__init__(self)

		if promotion_model:
			self._init_promotion_slot_from_model(promotion_model)

	def _get_detail_data(self):
		return {
			'count': self.count,
			'is_enable_cycle_mode': self.is_enable_cycle_mode,
			'premium_products': self.premium_products
		}