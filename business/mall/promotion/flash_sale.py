# -*- coding: utf-8 -*-
"""@package business.mall.promotion.flash_sale
限时抢购

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime, timedelta

from wapi.decorators import param_required
#from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from core.watchdog.utils import watchdog_alert
from business import model as business_model
import settings
from business.mall.promotion import promotion
from business.mall.promotion.promotion_result import PromotionResult
from business.mall.promotion.promotion_failure import PromotionFailure


class FlashSale(promotion.Promotion):
	"""
	限时抢购
	"""
	__slots__ = (
		'limit_period',
		'promotion_price',
		'count_per_purchase',
		'count_per_period'
	)

	def __init__(self, promotion_model=None):
		promotion.Promotion.__init__(self)
		self.type_name = 'flash_sale'

		if promotion_model:
			self._init_promotion_slot_from_model(promotion_model)

	def _get_detail_data(self):
		return {
			'limit_period': self.limit_period,
			'promotion_price': self.promotion_price,
			'count_per_purchase': self.count_per_purchase,
			'count_per_period': self.count_per_period
		}

	def allocate(self, webapp_user, product):
		"""
		检查促销是否可以使用
		"""
		#检查count_per_purchase		
		if product.purchase_count > self.count_per_purchase:
			return [PromotionFailure({
				'type': 'promotion:flash_sale:exceed_count_per_purchase',
				'msg': u'限购%d件' % self.count_per_purchase,
				'short_msg': u'限购%d件' % self.count_per_purchase,
			})]

		# #检查是否超过了限购周期的限制
		# if self.limit_period == 0 or self.limit_period == -1:
		# 	pass
		# else:
		# 	delta = datetime.today() - timedelta(days=self.limit_period)
		# 	purchase_record_count = mall_models.OrderHasPromotion.select().join(mall_models.Order).filter(
		# 		mall_models.OrderHasPromotion.webapp_user_id==webapp_user.id,
		# 		mall_models.OrderHasPromotion.promotion_id==self.id,
		# 		mall_models.OrderHasPromotion.created_at>=delta,
		# 		mall_models.Order.status!=mall_models.ORDER_STATUS_CANCEL
		# 	).count()
		#
		#检查是否超过了限购周期的限制

		# 限购周期，如果没有设置限购周期则表示整个活动周期
		delta = datetime.today() - timedelta(days=self.limit_period) if self.limit_period > 0 else 0
		# 限购周期内的限购次数
		if not(self.limit_period == 0 or self.limit_period == -1) and self.count_per_period == 0:
			# 仅设置限购周期
			limit_count_in_period = 1
		else:
			limit_count_in_period = self.count_per_period

		if limit_count_in_period or delta:

			purchase_record_count_query = mall_models.OrderHasPromotion.select().join(mall_models.Order).filter(
				mall_models.OrderHasPromotion.webapp_user_id==webapp_user.id,
				mall_models.OrderHasPromotion.promotion_id==self.id,
				mall_models.Order.status!=mall_models.ORDER_STATUS_CANCEL
			)
			if delta:
				purchase_record_count_query = purchase_record_count_query.filter(mall_models.OrderHasPromotion.created_at>=delta)

			purchase_record_count = purchase_record_count_query.count()

			# 限购周期内超过购买限制次数
			if purchase_record_count >= limit_count_in_period:
				return [PromotionFailure({
					'type': 'promotion:flash_sale:limit_period',
					'msg': u'在限购周期内不能多次购买',
					'short_msg': u'限制购买'
				})]

		return [PromotionResult()]

	def can_apply_promotion(self, promotion_product_group):
		return True

	def apply_promotion(self, promotion_product_group, purchase_info=None):
		#限时抢购只有一个product
		product = promotion_product_group.products[0]
		detail = {
			'limit_period': self.limit_period,
			'promotion_price': self.promotion_price,
			'promotioned_product_price': self.promotion_price,  #为了兼容weapp后端系统，此字段在apiserver中无用
			'count_per_purchase': self.count_per_purchase,
			'count_per_period': self.count_per_period
		}
		saved_money = product.original_price - self.promotion_price
		subtotal = product.purchase_count * product.price

		promotion_result = PromotionResult(saved_money=saved_money, subtotal=subtotal, detail=detail)

		return promotion_result

	def after_from_dict(self):
		self.type_name = 'flash_sale'