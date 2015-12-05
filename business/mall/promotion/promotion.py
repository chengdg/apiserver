# -*- coding: utf-8 -*-
"""@package business.mall.promotion.promotion
促销

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


class Promotion(business_model.Model):
	"""
	促销
	"""
	__slots__ = (
		'id',
		'owner_id',
		'type',
		'display_type',
		'type_name',
		'name',
		'promotion_title',
		'status',
		'display_status',
		'start_date',
		'end_date',
		'member_grade_id',
		'created_at'
	)

	def __init__(self):
		business_model.Model.__init__(self)

	def _init_promotion_slot_from_model(self, promotion_model):
		self._init_slot_from_model(promotion_model, Promotion.__slots__)
		self.start_date = self.start_date.strftime("%Y-%m-%d %H:%M")
		self.end_date = self.end_date.strftime("%Y-%m-%d %H:%M")
		self.created_at = self.created_at.strftime("%Y-%m-%d %H:%M")
		self.display_status = promotion_models.PROMOTIONSTATUS2NAME.get(self.status, u'未知')
		self.display_type = promotion_models.PROMOTION2TYPE.get(self.type, {'display_name':u'未知'})['display_name']
		self.type_name = promotion_models.PROMOTION2TYPE.get(self.type, {'name':u'unknown'})['name']

		self.context['detail_id'] = promotion_model.detail_id

	def _after_fill_specific_detail(self):
		pass

	def fill_specific_detail(self, specific_model):
		"""
		填充促销特定信息
		"""
		if specific_model:
			self._init_slot_from_model(specific_model)

		self._after_fill_specific_detail()

	def is_active(self):
		"""
		判断促销当前是否有效
		"""
		if self.status == promotion_models.PROMOTION_STATUS_FINISHED or self.status == promotion_models.PROMOTION_STATUS_DELETED:
			return False

		#self.__update_status_if_necessary()

		now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		if self.start_date > now:
			return False
		if self.end_date < now:
			return False

		return True

	def _get_detail_data(self):
		raise RuntimeError("_get_detail_data must be implemented by Promotion's subclass " + str(type(self)))

	@property
	def detail(self):
		return self._get_detail_data()

	@property
	def DetailClass(self):
		"""
		[property] 促销的detail类
		"""
		if self.type == promotion_models.PROMOTION_TYPE_FLASH_SALE:
			return promotion_models.FlashSale
		elif self.type == promotion_models.PROMOTION_TYPE_PRICE_CUT:
			return promotion_models.PriceCut
		elif self.type == promotion_models.PROMOTION_TYPE_INTEGRAL_SALE:
			return promotion_models.IntegralSale
		elif self.type == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
			return promotion_models.PremiumSale
		elif self.type == promotion_models.PROMOTION_TYPE_COUPON:
			return promotion_models.CouponRule
		else:
			return None

	def to_dict(self):
		data = {}
		data.update(super(Promotion, self).to_dict(Promotion.__slots__))
		data.update(super(Promotion, self).to_dict(self.__slots__))
		data['detail'] = self.detail

		return data

	@classmethod
	def from_dict(cls, dict):
		slots = []
		slots.extend(Promotion.__slots__)
		slots.extend(cls.__slots__)

		instance = cls()
		for slot in slots:
			value = dict.get(slot, None)

			setattr(instance, slot, value)
		instance.after_from_dict()
		return instance