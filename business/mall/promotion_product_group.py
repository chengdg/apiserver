# -*- coding: utf-8 -*-
"""@package business.mall.promotion_product_group

一个PromotionProductGroup是一组product的集合，它们拥有同一个促销信息。

比如购买同一个商品的不同规格，它们都拥有同一个促销活动，因此在一个PromotionProductGroup中。

"""

import json
from bs4 import BeautifulSoup
import math
import itertools
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.mall.order_products import OrderProducts


class PromotionProductGroup(business_model.Model):
	"""按促销分组的商品group
	"""
	__slots__ = (
		"id",
		"uid",
		"promotion_type",
		'products',
		'promotion',
		'promotion_result',
		'promotion_saved_money',
		'integral_sale',
		'integral_sale_rule',
		'active_integral_sale_rule',
		'can_use_promotion',
		'promotion_json',
		'member_grade_id'
	)

	def __init__(self, group_info):
		business_model.Model.__init__(self)

		self.id = group_info['id']
		self.uid = group_info['uid']
		self.products = group_info['products']
		self.can_use_promotion = False
		self.promotion_type = group_info['promotion_type']
		self.promotion = group_info['promotion']
		self.integral_sale = group_info['integral_sale']
		self.promotion_result = None
		self.integral_sale_rule = False
		self.member_grade_id = group_info['member_grade_id']
		
		self.promotion_saved_money = 0.0

		self.promotion_json = json.dumps(self.promotion.to_dict()) if self.promotion else json.dumps(None)

		if self.integral_sale:
			self.integral_sale_rule = True

			#设置每个商品的active_integral_sale_rule
			self.active_integral_sale_rule = self.integral_sale.get_rule_for(self.member_grade_id)
			for product in self.products:
				product.active_integral_sale_rule = self.active_integral_sale_rule

	def apply_promotion(self, purchase_info=None):
		"""
		执行促销活动
		"""
		if self.promotion:
			self.can_use_promotion, self.promotion_result = self.promotion.apply_promotion(self, purchase_info)
			if not self.can_use_promotion:
				self.promotion = None
				self.promotion_result = None
				for product in self.products:
					product.disable_promotion()
			else:
				self.promotion_saved_money = self.promotion_result.get('saved_money', 0.0)
				for product in self.products:
					product.set_promotion_result(self.promotion_result)
		else:
			if purchase_info:
				if purchase_info.group2integralinfo and (self.uid in purchase_info.group2integralinfo):
					#当前product group存在is_permanant_active的积分应用
					#TODO2: 在前端react重构完成后，这里要重新设计实现，目前硬编码实现
					product = self.products[0]
					promotion_ids = [relation.promotion_id for relation in promotion_models.ProductHasPromotion.select().dj_where(product_id=product.id)]
					integral_sale_detail_ids = [promotion.detail_id for promotion in promotion_models.Promotion.select().dj_where(type=promotion_models.PROMOTION_TYPE_INTEGRAL_SALE, id__in=promotion_ids)]
					has_permanant_integral_sale = promotion_models.IntegralSale.select().dj_where(id__in=integral_sale_detail_ids, is_permanant_active=True).count() > 0
					if has_permanant_integral_sale:
						integral_info = purchase_info.group2integralinfo[self.uid]
						self.active_integral_sale_rule = {
							'discount': 100
						}
						self.promotion_result = {
							'integral_money': integral_info['money'],
							'use_integral': integral_info['integral']
						}

	def to_dict(self, with_price_factor=False, with_coupon_info=False):
		"""获取promotion product group的json数据

		无论self.products中的product是Product, OrderProduct, 还是ShoppingCartProduct，
		我们都通过其product.to_dict来获取其json数据
		"""
		data = self.context.get('_data', None)
		if not data:
			data = {
				'id': self.id,
				'promotion_type': self.promotion_type,
				'can_use_promotion': self.can_use_promotion,
				'promotion': self.promotion.to_dict() if self.promotion else None,
				'promotion_result': self.promotion_result,
				'integral_sale_rule': self.integral_sale_rule
			}

			product_datas = []
			for product in self.products:
				#根据product类型的不同(Product, OrderProduct, ShoppingCartProduct), to_dict的结果也不同
				product_datas.append(product.to_dict())

			data['products'] = product_datas

			self.context['_data'] = data

		if with_price_factor:
			if not 'price_factor' in data:
				data['price_factor'] = self.__get_price_factor(with_coupon_info)

		return data

	def __get_price_factor(self, with_coupon_info=False):
		"""获取每一个product group用于前端计算价格的price factor

		每一个price factor为计算商品的价格需要参考的因子
		"""
		price_factor = self.context.get('_price_factor', None)
		if not price_factor:
			product_factors = []
			for product in self.products:
				product_factors.append({
					"id": product.id,
					"model": product.model_name,
					"count": product.purchase_count,
					"price": product.price,
					"original_price": product.original_price,
					"weight": product.weight,
					"active_integral_sale_rule": getattr(product, 'active_integral_sale_rule', None),
					"postageConfig": product.postage_config,
					"forbidden_coupon": (not product.can_use_coupon) if with_coupon_info else False
				})

			factor = {
				'id': self.id,
				'uid': self.uid,
				'products': product_factors,
				'promotion': self.promotion.to_dict() if self.promotion else None,
				'promotion_type': self.promotion_type,
				'promotion_result': self.promotion_result,
				'integral_sale_rule': self.integral_sale_rule,
				'can_use_promotion': self.can_use_promotion
			}
			self.context['_price_factor'] = factor

		return factor



