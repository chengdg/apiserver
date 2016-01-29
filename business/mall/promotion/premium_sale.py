# -*- coding: utf-8 -*-
"""@package business.mall.promotion.premium_sale
买赠

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
#from wapi import wapi_utils
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
		premium_result.stocks = None
		premium_result.model_name = None
		premium_result.pic_url = '%s%s' % (settings.IMAGE_HOST, product['thumbnails_url']) if product['thumbnails_url'].find('http') == -1 else product['thumbnails_url']

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
				if stock_info['stock_type'] == mall_models.PRODUCT_STOCK_TYPE_UNLIMIT:
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
		failed_reasons = []
		updated_premium_products = []
		for premium_product in self.premium_products:
			premium_product_id = premium_product['id']
			stocks = product2stocks.get(premium_product_id, -2)
			if stocks == -2:
				#没有库存信息
				pass
			elif stocks == -1:
				#无限库存
				pass
			elif stocks == 0:
				if webapp_user.is_force_purchase():
					#强制购买，改变赠品数量
					premium_product['premium_count'] = 0
					premium_product['count'] = premium_product['premium_count']
				else:
					reason = PromotionFailure({
						'type': 'promotion:premium_sale:no_premium_product_stocks',
						'msg': u'已赠完',
						'short_msg': u'已赠完'
					})
					self.__supply_product_info_into_fail_reason(premium_product, reason)
					failed_reasons.append(reason)
			elif premium_product['premium_count'] > stocks:
				if webapp_user.is_force_purchase():
					#强制购买，改变赠品数量
					premium_product['premium_count'] = stocks
					premium_product['count'] = premium_product['premium_count']
					#商品库存小于赠品，直接将库存设置为0
					mall_models.ProductModel.update(stocks=0).dj_where(product_id=premium_product['premium_product_id'], name='standard').execute()
				else:
					reason = PromotionFailure({
						'type': 'promotion:premium_sale:not_enough_premium_product_stocks',
						'msg': u'库存不足',
						'short_msg': u'库存不足'
					})
					self.__supply_product_info_into_fail_reason(premium_product, reason)
					failed_reasons.append(reason)
			else:
				#商品库存大于赠品，直接扣库存
				try:
					mall_models.ProductModel.update(stocks=mall_models.ProductModel.stocks-premium_product['premium_count']).dj_where(product_id=premium_product['premium_product_id'], name='standard').execute()
					updated_premium_products.append(premium_product)
				except:
					reason = PromotionFailure({
						'type': 'promotion:premium_sale:not_enough_premium_product_stocks',
						'msg': u'库存不足',
						'short_msg': u'库存不足'
					})
					self.__supply_product_info_into_fail_reason(premium_product, reason)
					failed_reasons.append(reason)

		if len(failed_reasons) > 0:
			return failed_reasons
		else:
			result = PromotionResult()
			result.updated_premium_products = updated_premium_products
			result.need_disable_discount = True #买赠活动需要禁用会员折扣
			return [result]

	def can_apply_promotion(self, promotion_product_group):
		can_use_promotion = True

		total_purchase_count = 0
		for product in promotion_product_group.products:
			total_purchase_count += product.purchase_count

		if total_purchase_count < self.count:
			can_use_promotion = False

		return can_use_promotion

	def __make_compatible_to_old_version(self, purchase_info, premium_products):
		"""
		兼容老的数据格式（后台管理系统会使用）
		"""
		from business.mall.product import Product
		webapp_owner = purchase_info.webapp_owner
		for premium_product in self.premium_products:
			premium_product['count'] = premium_product['premium_count']
			product = Product.from_id({
				'webapp_owner': webapp_owner,
				'product_id': premium_product['premium_product_id']
			})
			premium_product['price'] = product.price_info['min_price']
			# premium_product['supplier'] = product.supplier

	def apply_promotion(self, promotion_product_group, purchase_info=None):
		products = promotion_product_group.products
		first_product = products[0]
		promotion = first_product.promotion
		promotion_detail = promotion.detail

		total_purchase_count = 0
		total_product_price = 0.0
		for product in products:
			total_purchase_count += product.purchase_count
			# 买赠优先于会员价，使用原价计算“小计”
			total_product_price += product.original_price * product.purchase_count

		#如果满足循环满赠，则调整赠品数量
		if self.is_enable_cycle_mode:
			premium_round_count = total_purchase_count / self.count
			for premium_product in self.premium_products:
				premium_product['premium_count'] = premium_product['premium_count'] * premium_round_count

		if purchase_info:
			#当purchase_info有效，表示在下单上下文中，存储的数据需要兼容后台管理系统
			self.__make_compatible_to_old_version(purchase_info, self.premium_products)

		detail = {
			'count': self.count,
			'is_enable_cycle_mode': self.is_enable_cycle_mode,
			'promotion_price': -1,
			'premium_products': self.premium_products
		}
		promotion_result = PromotionResult(saved_money=0, subtotal=total_product_price, detail=detail)
		promotion_result.need_disable_discount = True
		return promotion_result

	def after_from_dict(self):
		self.type_name = 'premium_sale'

	def get_detail(self,promotion_product_group, purchase_info=None):

		products = promotion_product_group.products

		total_purchase_count = 0
		total_product_price = 0.0
		for product in products:
			total_purchase_count += product.purchase_count
			# 买赠优先于会员价，使用原价计算“小计”
			total_product_price += product.price * product.purchase_count


		detail = {
			'count': self.count,
			'is_enable_cycle_mode': self.is_enable_cycle_mode,
			'promotion_price': -1,
			'premium_products': self.premium_products
		}
		promotion_result = PromotionResult(saved_money=0, subtotal=total_product_price, detail=detail)
		return promotion_result