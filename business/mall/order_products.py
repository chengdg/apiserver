# -*- coding: utf-8 -*-
"""@package business.mall.order_products
订单商品(OrderPdocut)集合

OrderProducts用于构建一组OrderProduct，OrderProducts存在的目的是为了后续优化，以最少的数据库访问次数对商品信息进行批量填充

"""

import json
from bs4 import BeautifulSoup
import math
import itertools

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.order_product import OrderProduct 
from business.mall.forbidden_coupon_product_ids import ForbiddenCouponProductIds
import settings


class OrderProducts(business_model.Model):
	"""订单商品集合
	"""
	__slots__ = (
		'products',
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'purchase_info'])
	def get(args):
		"""工厂方法，创建OrderProducts对象

		@param[in] purchase_info: 购买信息PurchaseInfo对象

		@return OrderProducts对象
		"""
		order_products = OrderProducts(args['webapp_owner'], args['webapp_user'])
		order_products.__get_products_from_purchase_info(args['purchase_info'])

		return order_products

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'order'])
	def get_for_order(args):
		"""工厂方法，根据Order创建OrderProducts对象

		@param[in] order: 购买信息PurchaseInfo对象

		@return OrderProducts对象
		"""
		order_products = OrderProducts(args['webapp_owner'], args['webapp_user'])
		order_products.__get_products_for_order(args['order'])

		return order_products

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

	def __get_products_from_purchase_info(self, purchase_info):
		'''根据purchase info获取订单商品集合
		'''
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		product_ids = purchase_info.product_ids
		promotion_ids = purchase_info.promotion_ids
		product_counts = purchase_info.product_counts
		product_model_names = purchase_info.product_model_names
		self.products = []
		product_infos = []
		product2count = {}
		product2promotion = {}

		for i in range(len(product_ids)):
			product_id = int(product_ids[i])
			product_model_name = product_model_names[i]
			product_count = int(product_counts[i])
			product_promotion_id = promotion_ids[i] if promotion_ids[i] else 0
			product_info = {
				"id": product_id,
				"model_name": product_model_name,
				"count": product_count,
				"promotion_id": product_promotion_id
			}
			self.products.append(OrderProduct.get({
				"webapp_owner": webapp_owner,
				"webapp_user": webapp_user,
				"product_info": product_info
			}))
		
		#TODO2：目前对商品是否可使用优惠券的设置放在了order_products中，主要是出于目前批量处理的考虑，后续应该将r_forbidden_coupon_product_ids资源进行优化，将判断逻辑放入到order_product中
		forbidden_coupon_product_ids = ForbiddenCouponProductIds.get_for_webapp_owner({
			'webapp_owner': webapp_owner
		}).ids
		for product in self.products:
			if product.id in forbidden_coupon_product_ids:
				product.can_use_coupon = False

	def __get_products_for_order(self, order):
		'''根据order获取订单商品集合
		'''
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		self.products = []

		order_product_infos = [{
			'id': r.product_id,
			'model_name': r.product_model_name,
			'count': r.number,
			'promotion_id': r.promotion_id,
			'price': r.price,
			'total_price': r.total_price,
			'promotion_money': r.promotion_money,
			'discount_money': r.grade_discounted_money
		} for r in mall_models.OrderHasProduct.select().dj_where(order=order.id)]
	
		for order_product_info in order_product_infos:
			self.products.append(OrderProduct.get({
				"webapp_owner": webapp_owner,
				"webapp_user": webapp_user,
				"product_info": order_product_info
			}))


