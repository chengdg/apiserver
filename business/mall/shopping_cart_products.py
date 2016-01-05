# -*- coding: utf-8 -*-
"""@package business.mall.shopping_cart_products
购物车商品(ShoppingCartPdocut)集合

ShoppingCartProducts用于构建一组ShoppingCartProduct，ShoppingCartProducts存在的目的是为了后续优化，以最少的数据库访问次数对商品信息进行批量填充

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
from business.mall.shopping_cart_product import ShoppingCartProduct 
import settings


class ShoppingCartProducts(business_model.Model):
	"""
	购物车商品集合
	"""
	__slots__ = (
		'products',
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def get_for_webapp_user(args):
		"""工厂方法，获取webapp_user对应的ShoppingCartProducts对象

		@param[in] webapp_owner
		@param[in] webapp_user

		@return ShoppingCartProducts对象
		"""
		shopping_cart_products = ShoppingCartProducts(args['webapp_owner'], args['webapp_user'])

		return shopping_cart_products

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		self.__get_products(webapp_owner, webapp_user)

	def __get_products(self, webapp_owner, webapp_user):
		'''获取商品集合
		'''
		shopping_cart_items = mall_models.ShoppingCart.select().dj_where(webapp_user_id = webapp_user.id)

		self.products = []
		for shopping_cart_item in shopping_cart_items:
			product_info = {
				'id': shopping_cart_item.product_id,
				'model_name': shopping_cart_item.product_model_name,
				'count': shopping_cart_item.count,
				'shopping_cart_id': shopping_cart_item.id
			}

			shopping_cart_product = ShoppingCartProduct.get({
				'webapp_owner': webapp_owner,
				'webapp_user': webapp_user,
				'product_info': product_info
			})

			self.products.append(shopping_cart_product)


