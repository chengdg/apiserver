# -*- coding: utf-8 -*-
"""@package business.mall.promotion.flash_sale
限时抢购

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


class FlashSale(promotion.Promotion):
	"""
	限时抢购
	"""
	__slots__ = (
		'limit_period',
		'promotion_price',
		'count_per_purchase'
	)

	def __init__(self, promotion_model=None):
		promotion.Promotion.__init__(self)

		if promotion_model:
			self._init_promotion_slot_from_model(promotion_model)

	def _get_detail_data(self):
		return {
			'limit_period': self.limit_period,
			'promotion_price': self.promotion_price,
			'count_per_purchase': self.count_per_purchase
		}
