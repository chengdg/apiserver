# -*- coding: utf-8 -*-
"""@package business.mall.shopping_cart
购物车业务对象

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
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model
import settings
from business.decorator import cached_context_property
from business.mall.shopping_cart_products import ShoppingCartProducts
from business.mall.product_grouper import ProductGrouper


class ShoppingCart(business_model.Model):
	__slots__ = [
		'items', 
		'webapp_user',
	]

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def get_for_webapp_user(args):
		"""
		工厂方法，获取webapp_user对应的ShoppingCart业务对象

		@param[in] webapp_user

		@return ShoppingCart业务对象
		"""
		shopping_cart = ShoppingCart(args['webapp_owner'], args['webapp_user'])

		return shopping_cart

	def __init__(self, webapp_owner=None, webapp_user=None):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.webapp_user = webapp_user

	def add_product(self, product_id, product_model_name, count):
		"""
		向购物车中增加一个商品项

		@param[in] product_id: 商品id
		@param[in] product_model_name: 商品规格名
		@param[in] count: 商品数量
		"""
		try:
			shopping_cart_item = mall_models.ShoppingCart.get(
				mall_models.ShoppingCart.webapp_user_id == self.webapp_user.id,
				mall_models.ShoppingCart.product == product_id,
				mall_models.ShoppingCart.product_model_name == product_model_name
			)
			shopping_cart_item.count = shopping_cart_item.count + count
			shopping_cart_item.save()
		except:
			mall_models.ShoppingCart.create(
				webapp_user_id = self.webapp_user.id,
				product = product_id,
				product_model_name = product_model_name,
				count = count
			)

	@property
	def product_count(self):
		"""
		[property] 购物车中的商品数量

		@return 不同商品的数量，注意：如果有商品A（1个），商品B（3个），则返回2，而不是4
		"""
		return mall_models.ShoppingCart.select().dj_where(webapp_user_id=self.webapp_user.id).count()

	@cached_context_property
	def __products(self):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.webapp_user
		shopping_cart_products = ShoppingCartProducts.get_for_webapp_user({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user
		})

		products = shopping_cart_products.products

		valid_products = []
		invalid_products = []
		for product in products:
			import logging
			if product.shelve_type == mall_models.PRODUCT_SHELVE_TYPE_OFF or \
				product.shelve_type == mall_models.PRODUCT_SHELVE_TYPE_RECYCLED or\
				product.is_deleted or \
				(product.stock_type == mall_models.PRODUCT_STOCK_TYPE_LIMIT and product.stocks == 0) or\
				product.is_model_deleted:
				#or\ (shopping_cart_item.product_model_name == 'standard' and product.is_use_custom_model):
				invalid_products.append(product)
			else:
				valid_products.append(product)

		return valid_products, invalid_products

	@cached_context_property
	def product_groups(self):
		"""
		[property] 有效商品集合按促销进行分组后的product group列表

		@return PromotionProductGroup集合经过to_dict转换后的数据list
		"""
		valid_products, _ = self.__products

		product_grouper = ProductGrouper()
		promotion_product_groups = product_grouper.group_product_by_promotion(self.webapp_user.member, valid_products)
		product_group_datas = [group.to_dict(with_price_factor=True) for group in promotion_product_groups]

		return product_group_datas

	@cached_context_property
	def invalid_products(self):
		"""
		[property] 购物车中已经失效的商品

		@return 失效的ShoppingCartProduct集合
		"""
		_, invalid_products = self.__products

		return invalid_products

	def delete_items(self, ids):
		"""
		删除一组购物车项

		@param[in] ids: 购物车项的id集合
		"""
		mall_models.ShoppingCart.delete().dj_where(id__in=ids).execute()




