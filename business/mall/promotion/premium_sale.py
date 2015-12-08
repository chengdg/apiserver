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
	买赠
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

	def apply_promotion(self, products):
		first_product = products[0]
		promotion = first_product.promotion
		promotion_detail = promotion.detail
		can_use_promotion = True

		total_purchase_count = 0
		total_product_price = 0.0
		for product in products:
			total_purchase_count += product.purchase_count
			total_product_price += product.price * product.purchase_count

		if total_purchase_count < self.count:
			can_use_promotion = False
		else:
			#如果满足循环满赠，则调整赠品数量
			if self.is_enable_cycle_mode:
				premium_round_count = total_purchase_count / self.count
				for premium_product in self.premium_products:
					premium_product['premium_count'] = premium_product['premium_count'] * premium_round_count

		promotion_result = {
			"subtotal": total_product_price
		}

		return True, promotion_result