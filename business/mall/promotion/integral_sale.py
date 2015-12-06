# -*- coding: utf-8 -*-
"""@package business.mall.promotion.integral_sale
积分应用

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
from business.mall.promotion.integral_sale_rule import IntegralSaleRule


class IntegralSale(promotion.Promotion):
	"""
	积分应用
	"""
	__slots__ = (
		'integral_sale_type',
		'display_integral_sale_type',
		'is_permanant_active',
		'rules',
		'discount',
		'discount_money'
	)

	def __init__(self, promotion_model=None):
		promotion.Promotion.__init__(self)

		if promotion_model:
			self._init_promotion_slot_from_model(promotion_model)

	def _after_fill_specific_detail(self):
		self.display_integral_sale_type = u'部分抵扣' if self.type == promotion_models.INTEGRAL_SALE_TYPE_PARTIAL else u'全额抵扣'

	def _get_detail_data(self):
		return {
			'type': self.integral_sale_type,
			'type_name': self.display_integral_sale_type,
			'is_permanant_active': self.is_permanant_active,
			'rules': self.rules,
			'discount': self.discount,
			'discount_money': self.discount_money
		}

	def add_rule(self, integral_sale_rule_model):
		"""
		向integral sale促销中添加`积分应用规则`

		Parameters
			[in] integral_sale_rule_model: mall_models.IntegralSaleRule model的对象实例
		"""
		if self.rules is None:
			self.rules = []

		rule = IntegralSaleRule(integral_sale_rule_model)
		self.rules.append(rule.to_dict())

	def calculate_discount(self):
		"""
		计算折扣信息
		"""
		if len(self.rules) == 0:
			discount = 0
			discount_money = 0
		elif len(self.rules) == 1:
			rule = self.rules[0]
			discount = str(rule['discount']) + '%'
			discount_money = "%.2f" % rule['discount_money']
		else:
			discounts = [rule['discount'] for rule in self.rules]
			max_discount = max(discounts)
			min_discount = min(discounts)

			discount_moneys = [rule['discount_money'] for rule in self.rules]
			max_discount_money = max(discount_moneys)
			min_discount_money = min(discount_moneys)

			if max_discount == min_discount:
				discount = str(max_discount)
			else:
				discount = '%d%% ~ %d%%' % (min_discount, max_discount)

			if max_discount_money == min_discount_money:
				discount_money = str(max_discount_money)
			else:
				discount_money = '%.2f ~ %.2f' % (min_discount_money, max_discount_money)

		self.discount = discount
		self.discount_money = discount_money

	def apply_promotion(self, products):
		return True, None