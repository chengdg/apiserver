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
from business.mall.realtime_stock import RealtimeStock
from business.mall.promotion.promotion_result import PromotionResult
from business.mall.promotion.promotion_failure import PromotionFailure


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

		self.type_name = 'premium_sale'

	def _get_detail_data(self):
		return {
			'count': self.count,
			'is_enable_cycle_mode': self.is_enable_cycle_mode,
			'premium_products': self.premium_products
		}

	def __supply_product_info_into_fail_reason(self, product, premium_result):
		premium_result.id = product['id']
		premium_result.name = product['name']
		premium_result.stocks = 0
		premium_result.model_name = ""
		premium_result.pic_url = product['thumbnails_url']

	def allocate(self, webapp_user, product):
		#收集赠品的所有库存，可能的结果有：
		#	-1: 无限库存
		#	-2: 没有库存信息
		#	n: 有限库存
		product2stocks = {}
		for premium_product in self.premium_products:
			premium_product_id = premium_product['id']
			realtime_stock = RealtimeStock.from_product_id({
				'product_id': premium_product_id
			})
			model2stock = realtime_stock.model2stock
			for model, stock_info in model2stock.items():
				if stock_info['stock_type'] == 0:
					product2stocks[premium_product_id] = -1
				else:
					if premium_product_id in product2stocks:
						if product2stocks[premium_product_id] == -1:
							#已识别出是无限库存
							pass
						else:
							product2stocks[premium_product_id] = product2stocks.get(premium_product_id, 0) + stock_info['stocks']
					else:
						product2stocks[premium_product_id] = stock_info['stocks']

		#检查赠品库存是否满足
		for premium_product in self.premium_products:
			premium_product_id = premium_product['id']
			stocks = product2stocks.get(premium_product_id, -2)
			if stocks == -2:
				#没有库存信息
				pass
			elif stocks == -1:
				#无限库存
				pass
			elif stocks == 0 or premium_product['premium_count'] > stocks:
				reason = PromotionFailure({
					'type': 'promotion:premium_sale:not_enough_premium_product_stocks',
					'msg': u'库存不足',
					'short_msg': u'库存不足'
				})
				self.__supply_product_info_into_fail_reason(premium_product, reason)
				return reason

		#禁用商品会员价
		#product.disable_discount()

		result = PromotionResult()
		result.need_disable_discount = True
		return result

	def can_apply_promotion(self, promotion_product_group):
		can_use_promotion = True

		total_purchase_count = 0
		for product in promotion_product_group.products:
			total_purchase_count += product.purchase_count

		if total_purchase_count < self.count:
			can_use_promotion = False

		return can_use_promotion

	def apply_promotion(self, promotion_product_group, purchase_info=None):
		products = promotion_product_group.products
		first_product = products[0]
		promotion = first_product.promotion
		promotion_detail = promotion.detail

		total_purchase_count = 0
		total_product_price = 0.0
		for product in products:
			total_purchase_count += product.purchase_count
			total_product_price += product.price * product.purchase_count

		#如果满足循环满赠，则调整赠品数量
		if self.is_enable_cycle_mode:
			premium_round_count = total_purchase_count / self.count
			for premium_product in self.premium_products:
				premium_product['premium_count'] = premium_product['premium_count'] * premium_round_count

		detail = {
			'count': self.count,
			'is_enable_cycle_mode': self.is_enable_cycle_mode,
			'promotion_price': -1,
			'premium_products': self.premium_products
		}
		promotion_result = PromotionResult(saved_money=0, subtotal=total_product_price, detail=detail)
		return promotion_result

	def after_from_dict(self):
		self.type_name = 'premium_sale'