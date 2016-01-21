# -*- coding: utf-8 -*-
"""@package business.mall.reserved_products
已预订商品(ReservedProductRepository)资源库

ReservedProductRepository用于获取一组ReservedProduct，ReservedProductRepository能进行批量获取优化，以最少的数据库访问次数对商品信息进行批量填充

"""

import json
from bs4 import BeautifulSoup
import math
import itertools

from wapi.decorators import param_required
#from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.reserved_product import ReservedProduct 
from business.mall.forbidden_coupon_product_ids import ForbiddenCouponProductIds
import settings


class ReservedProductRepository(business_model.Model):
	"""
	已预订商品集合
	"""
	__slots__ = ()

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def get(args):
		"""工厂方法，获取repository对象

		@param[in] webapp_owner
		@param[in] webapp_user

		@return ReservedProductRepository对象
		"""
		repository = ReservedProductRepository(args['webapp_owner'], args['webapp_user'])
		
		return repository

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

	def get_shopping_cart_reserved_products(self, shopping_cart):
		"""
		获取购物车中的已订购商品集合

		Parameters
			[in] shopping_cart: ShoppingCart对象

		Returns
			ReservedProduct对象集合
		"""
		products = []
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']
		for shopping_cart_item in shopping_cart.items:
			product_info = {
				'id': shopping_cart_item.product_id,
				'model_name': shopping_cart_item.product_model_name,
				'count': shopping_cart_item.count,
				'shopping_cart_id': shopping_cart_item.id
			}

			reserved_product = ReservedProduct.get({
				'webapp_owner': webapp_owner,
				'webapp_user': webapp_user,
				'product_info': product_info
			})

			products.append(reserved_product)

		return products

	def get_reserved_products_from_purchase_info(self, purchase_info):
		'''
		根据purchase info获取已预订商品集合

		@param [in] purchase_info: PurchaseInfo对象

		@return ReservedProduct对象集合
		'''
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		product_ids = purchase_info.product_ids
		promotion_ids = purchase_info.promotion_ids
		product_counts = purchase_info.product_counts
		product_model_names = purchase_info.product_model_names
		products = []
		
		for i in range(len(product_ids)):
			product_id = int(product_ids[i])
			expected_promotion_id = int(promotion_ids[i])
			product_model_name = product_model_names[i]
			product_count = int(product_counts[i])
			product_info = {
				"id": product_id,
				"model_name": product_model_name,
				"count": product_count,
				"expected_promotion_id": expected_promotion_id
			}
			products.append(ReservedProduct.get({
				"webapp_owner": webapp_owner,
				"webapp_user": webapp_user,
				"product_info": product_info
			}))
		
		#TODO2：目前对商品是否可使用优惠券的设置放在了reserved_product_repository中
		#主要是出于目前批量处理的考虑，后续应该将判断逻辑放入到reserved_product中
		forbidden_coupon_product_ids = ForbiddenCouponProductIds.get_for_webapp_owner({
			'webapp_owner': webapp_owner
		}).ids
		for product in products:
			if product.id in forbidden_coupon_product_ids:
				product.can_use_coupon = False

		return products