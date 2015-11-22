# -*- coding: utf-8 -*-
"""@package business.mall.promotion_product_group
按照促销对product进行聚类

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
	"""按促销进行分组的商品分组
	"""
	__slots__ = (
		"id",
		"uid",
		"promotion_type",
		'products',
		'promotion',
		'promotion_result',
		'integral_sale_rule',
		'can_use_promotion',
		'promotion_json',
		'member_grade_id'
	)

	def __init__(self, group_info):
		business_model.Model.__init__(self)

		self.id = group_info['id']
		self.uid = group_info['uid']
		self.products = group_info['products']
		self.can_use_promotion = group_info['can_use_promotion']
		self.promotion_type = group_info['promotion_type']
		self.promotion = group_info['promotion']
		self.promotion_result = group_info['promotion_result']
		self.integral_sale_rule = group_info['integral_sale_rule']
		self.member_grade_id = group_info['member_grade_id']
		self.promotion_json = json.dumps(self.promotion)

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
				'promotion': self.promotion,
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
				'promotion': self.promotion,
				'promotion_type': self.promotion_type,
				'promotion_result': self.promotion_result,
				'integral_sale_rule': self.integral_sale_rule,
				'can_use_promotion': self.can_use_promotion
			}
			self.context['_price_factor'] = factor

		return factor



