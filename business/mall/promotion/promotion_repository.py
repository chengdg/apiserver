# -*- coding: utf-8 -*-
"""@package business.mall.promotion.promotion_repository
促销资源库

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
from business.mall.promotion.flash_sale import FlashSale
from business.mall.promotion.premium_sale import PremiumSale
from business.mall.promotion.integral_sale import IntegralSale


class PromotionRepository(business_model.Model):
	"""
	促销资源库
	"""
	__slots__ = ()

	@staticmethod
	def __get_promotion_detail_class(promotion_type):
		"""
		获取促销特定数据对应的业务对象的class

		Parameters
			[in] promotion_type: 促销类型

		Returns
			促销特定数据的class（比如FlashSale）
		"""
		DetailClass = None
		if promotion_type == promotion_models.PROMOTION_TYPE_FLASH_SALE:
			DetailClass = promotion_models.FlashSale
		elif promotion_type == promotion_models.PROMOTION_TYPE_PRICE_CUT:
			DetailClass = promotion_models.PriceCut
		elif promotion_type == promotion_models.PROMOTION_TYPE_INTEGRAL_SALE:
			DetailClass = promotion_models.IntegralSale
		elif promotion_type == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
			DetailClass = promotion_models.PremiumSale
		elif promotion_type == promotion_models.PROMOTION_TYPE_COUPON:
			DetailClass = promotion_models.CouponRule

		return DetailClass

	@staticmethod
	def __fill_integral_sale_rule_details(integral_sales):
		"""
		填充与积分应用相关的`积分应用规则`
		"""
		integral_sale_ids = []
		id2sale = {}
		for integral_sale in integral_sales:
			integral_sale_detail_id = integral_sale.context['detail_id']
			integral_sale.rules = []
			integral_sale_ids.append(integral_sale_detail_id)
			id2sale[integral_sale_detail_id] = integral_sale

		integral_sale_rules = list(promotion_models.IntegralSaleRule.select().dj_where(integral_sale_id__in=integral_sale_ids))
		for integral_sale_rule in integral_sale_rules:
			integral_sale_id = integral_sale_rule.integral_sale_id
			id2sale[integral_sale_id].add_rule(integral_sale_rule)

		for integral_sale in integral_sales:
			integral_sale.calculate_discount()

	@staticmethod
	def __fill_premium_products_details(premium_sales):
		"""
		填充与限时抢购相关的`促销商品详情`
		"""
		premium_sale_ids = []
		id2sale = {}
		for premium_sale in premium_sales:
			prenium_sale_detail_id = premium_sale.context['detail_id']
			premium_sale.premium_products = []
			premium_sale_ids.append(prenium_sale_detail_id)
			id2sale[prenium_sale_detail_id] = premium_sale

		premium_sale_products = list(promotion_models.PremiumSaleProduct.select().dj_where(premium_sale_id__in=premium_sale_ids))
		product_ids = [premium_sale_product.product_id for premium_sale_product in premium_sale_products]
		products = mall_models.Product.select().dj_where(id__in=product_ids)
		id2product = dict([(product.id, product) for product in products])

		for premium_sale_product in premium_sale_products:
			premium_sale_id = premium_sale_product.premium_sale_id
			product_id = premium_sale_product.product_id
			product = id2product[product_id]
			data = {
				'id': product.id,
				'name': product.name,
				'thumbnails_url': '%s%s' % (settings.IMAGE_HOST, product.thumbnails_url),
				'original_premium_count': premium_sale_product.count,
				'premium_count': premium_sale_product.count,
				'premium_unit': premium_sale_product.unit
			}
			id2sale[premium_sale_id].premium_products.append(data)

	@staticmethod
	def __fill_specific_details(promotions):
		"""
		为促销填充促销特定数据

		Parameters:
			[in, out] promotions: 促销集合

		Note:
			针对不同的促销，会获取不同的促销特定数据的model对象（比如FlashSale），进行填充
		"""
		type2promotions = dict()
		for promotion in promotions:
			type2promotions.setdefault(promotion.type, []).append(promotion)

		for promotion_type, promotions in type2promotions.items():
			#确定detail的Model class
			DetailClass = PromotionRepository.__get_promotion_detail_class(promotion_type)

			#获取specific detail数据
			detail_ids = [promotion.context['detail_id'] for promotion in promotions]
			if DetailClass:
				detail_models = DetailClass.select().dj_where(id__in=detail_ids)
				id2detail = dict([(detail_model.id, detail_model) for detail_model in detail_models])
				for promotion in promotions:
					detail_model = id2detail[promotion.context['detail_id']]
					promotion.fill_specific_detail(detail_model)

				if promotion_type == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
					PromotionRepository.__fill_premium_products_details(promotions)
				elif promotion_type == promotion_models.PROMOTION_TYPE_INTEGRAL_SALE:
					PromotionRepository.__fill_integral_sale_rule_details(promotions)
			else:
				raise ValueError('DetailClass(None) is not valid')

	@staticmethod
	@param_required(['products'])
	def fill_for_products(args):
		products = args['products']
		today = datetime.today()
		product_ids = []
		id2product = {}
		for product in products:
			product_ids.append(product.id)
			id2product[product.id] = product

		#创建promotions业务对象集合
		product_promotion_relations = list(promotion_models.ProductHasPromotion.select().dj_where(product_id__in=product_ids))
		promotion_ids = list()
		promotion2product = dict()
		for relation in product_promotion_relations:
			promotion_ids.append(relation.promotion_id)
			promotion2product[relation.promotion_id] = relation.product_id

		promotion_db_models = list(promotion_models.Promotion.select().dj_where(id__in=promotion_ids))
		promotions = []
		for promotion_db_model in promotion_db_models:
			if promotion_db_model.type == promotion_models.PROMOTION_TYPE_FLASH_SALE:
				promotion = FlashSale(promotion_db_model)
			if promotion_db_model.type == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
				promotion = PremiumSale(promotion_db_model)
			if promotion_db_model.type == promotion_models.PROMOTION_TYPE_INTEGRAL_SALE:
				promotion = IntegralSale(promotion_db_model)
			if promotion.is_active():
				promotions.append(promotion)

		PromotionRepository.__fill_specific_details(promotions)

		#为所有的product设置product.promotion
		for promotion in promotions:
			product_id = promotion2product.get(promotion.id, None)
			if not product_id:
				continue

			product = id2product.get(product_id, None)
			if not product:
				continue

			product.promotion = promotion

	@staticmethod
	def from_id(promotion_id):
		if promotion_id <= 0:
			return None
			
		promotion_db_model = promotion_models.Promotion.get(id=promotion_id)
		if promotion_db_model.type == promotion_models.PROMOTION_TYPE_FLASH_SALE:
			promotion = FlashSale(promotion_db_model)
		if promotion_db_model.type == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
			promotion = PremiumSale(promotion_db_model)
		if promotion_db_model.type == promotion_models.PROMOTION_TYPE_INTEGRAL_SALE:
			promotion = IntegralSale(promotion_db_model)
		if not promotion.is_active():
			return None

		PromotionRepository.__fill_specific_details([promotion])

		return promotion

	@staticmethod
	def get_promotion_from_dict_data(data):
		promotion_type = data['type']

		if promotion_type == promotion_models.PROMOTION_TYPE_FLASH_SALE:
			DetailClass = FlashSale
		# elif promotion_type == promotion_models.PROMOTION_TYPE_PRICE_CUT:
		# 	DetailClass = promotion_models.PriceCut
		elif promotion_type == promotion_models.PROMOTION_TYPE_INTEGRAL_SALE:
		 	DetailClass = IntegralSale
		elif promotion_type == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
		 	DetailClass = PremiumSale
		# elif promotion_type == promotion_models.PROMOTION_TYPE_COUPON:
		# 	DetailClass = promotion_models.CouponRule

		promotion = DetailClass.from_dict(data)

		return promotion
