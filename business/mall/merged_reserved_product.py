# -*- coding: utf-8 -*-
"""@package business.mall.merged_reserved_product
将不同规格的同种商品合并后的已预订商品

"""

import json
from bs4 import BeautifulSoup
import math
import itertools

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
import settings


class MergedReservedProduct(business_model.Model):
	"""
	合并后的已预订商品

	合并的意思是将不同规格的同种商品合并为一个product对象，方便promotion进行可用性的判断。
	比如：很多promotion都会根据购买数量决定是否使用促销，而一个商品的购买数量应该包含所有规格的购买数量之和。
	"""
	__slots__ = (
		'id',
		'name',
		'stocks',
		'model_name',
		'thumbnails_url',
		'expected_promotion_id',
		'used_promotion_id',
		'promotion',
		'purchase_count'
	)

	def __init__(self):
		business_model.Model.__init__(self)
		self.purchase_count = 0

		self.context['products'] = []

	def add_product(self, reserved_product):
		"""
		添加商品

		@param[in] reserved_product: ReservedProduct对象
		"""
		if not self.id:
			self.id = reserved_product.id
			self.name = reserved_product.name
			self.model_name = reserved_product.model_name
			self.stocks = reserved_product.stocks
			self.thumbnails_url = reserved_product.thumbnails_url
			self.expected_promotion_id = reserved_product.expected_promotion_id
			self.used_promotion_id = reserved_product.used_promotion_id
			self.promotion = reserved_product.promotion

		self.context['products'].append(reserved_product)
		self.purchase_count += reserved_product.purchase_count

	def has_expected_promotion(self):
		"""
		判断已预订商品是否拥有预期的促销

		@return 如果拥有预期促销，返回True；否则，返回False
		"""
		return self.expected_promotion_id != 0

	def is_expected_promotion_active(self):
		"""
		判断预期促销是否还在进行中

		Returns
			如果预期促销还在进行中，返回True；否则，返回False
		"""
		return self.expected_promotion_id == self.used_promotion_id

	def disable_discount(self):
		"""
		禁用会员折扣
		"""
		for reserved_product in self.context['products']:
			reserved_product.disable_discount()
