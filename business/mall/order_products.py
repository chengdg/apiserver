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
#from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.order_product import OrderProduct 
from business.mall.forbidden_coupon_product_ids import ForbiddenCouponProductIds
from business.mall.promotion.promotion import Promotion
import settings


class OrderProducts(business_model.Model):
	"""订单商品集合
	"""
	__slots__ = (
		'products',
	)

	# @staticmethod
	# @param_required(['webapp_owner', 'webapp_user', 'purchase_info'])
	# def get(args):
	# 	"""工厂方法，创建OrderProducts对象

	# 	@param[in] purchase_info: 购买信息PurchaseInfo对象

	# 	@return OrderProducts对象
	# 	"""
	# 	order_products = OrderProducts(args['webapp_owner'], args['webapp_user'])
	# 	order_products.__get_products_from_purchase_info(args['purchase_info'])

	# 	return order_products

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

	# def __get_products_from_purchase_info(self, purchase_info):
	# 	'''根据purchase info获取订单商品集合
	# 	'''
	# 	webapp_owner = self.context['webapp_owner']
	# 	webapp_user = self.context['webapp_user']

	# 	product_ids = purchase_info.product_ids
	# 	promotion_ids = purchase_info.promotion_ids
	# 	product_counts = purchase_info.product_counts
	# 	product_model_names = purchase_info.product_model_names
	# 	self.products = []
	# 	product_infos = []
	# 	product2count = {}
	# 	product2promotion = {}

	# 	for i in range(len(product_ids)):
	# 		product_id = int(product_ids[i])
	# 		product_model_name = product_model_names[i]
	# 		product_count = int(product_counts[i])
	# 		product_promotion_id = promotion_ids[i] if promotion_ids[i] else 0
	# 		product_info = {
	# 			"id": product_id,
	# 			"model_name": product_model_name,
	# 			"count": product_count,
	# 			"promotion_id": product_promotion_id
	# 		}
	# 		self.products.append(OrderProduct.get({
	# 			"webapp_owner": webapp_owner,
	# 			"webapp_user": webapp_user,
	# 			"product_info": product_info
	# 		}))
		
	# 	#TODO2：目前对商品是否可使用优惠券的设置放在了order_products中，主要是出于目前批量处理的考虑，后续应该将r_forbidden_coupon_product_ids资源进行优化，将判断逻辑放入到order_product中
	# 	forbidden_coupon_product_ids = ForbiddenCouponProductIds.get_for_webapp_owner({
	# 		'webapp_owner': webapp_owner
	# 	}).ids
	# 	for product in self.products:
	# 		if product.id in forbidden_coupon_product_ids:
	# 			product.can_use_coupon = False

	def __get_products_for_order(self, order):
		'''根据order获取订单商品集合
		'''
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		self.products = []

		id2promotion = dict([(r.promotion_id, r) for r in mall_models.OrderHasPromotion.select().dj_where(order=order.id)])

		order_product_infos = []	
		for r in mall_models.OrderHasProduct.select().dj_where(order=order.id):
			promotion = id2promotion.get(r.promotion_id, None)
			if promotion:
				promotion_result = json.loads(promotion.promotion_result_json)
				promotion_result['type'] = promotion.promotion_type
			else:
				promotion_result = None

			order_product_infos.append({
				'rid': r.id,
				'id': r.product_id,
				'model_name': r.product_model_name,
				'count': r.number,
				'promotion_id': r.promotion_id,
				'price': r.price,
				'total_price': r.total_price,
				'promotion_money': r.promotion_money,
				'discount_money': r.grade_discounted_money,
				'promotion_result': promotion_result,
				'integral_sale_id': r.integral_sale_id
			})
		order_product_infos.sort(lambda x,y: cmp(x['rid'], y['rid']))
	
		#按商品id收集购买商品集合{id1: [product1_model1, product1_model2, ...], id2: []}
		id2products = {}
		index = 0
		for order_product_info in order_product_infos:
			index += 1
			order_product = OrderProduct.get({
				"webapp_owner": webapp_owner,
				"webapp_user": webapp_user,
				"product_info": order_product_info
			})

			products_info = id2products.get(order_product.id, None)
			if products_info:
				products_info['products'].append(order_product)
			else:
				id2products[order_product.id] = {
					"index": index,
					"products": [order_product]
				}

		#根据promotion_id获取promotion_result
		items = id2products.items()
		items.sort(lambda x,y: cmp(x[1]["index"], y[1]["index"]))
		for product_id, products_info in items:
			products = products_info["products"]
			self.products.extend(products)

			#查看是否是买赠，如果是买赠，将赠品放入products
			first_product = products[0]
			promotion_id = first_product.used_promotion_id
			promotion = id2promotion.get(promotion_id, None)
			if not promotion:
				continue

			if promotion.promotion_type == 'premium_sale':
				#将premium_product转换为order product
				promotion_result = json.loads(promotion.promotion_result_json)
				promotion_result_version = promotion_result.get('version', '0')

				# 兼容weapp少量遗留订单产生错误数据，使得手机端和后台显示一致
				if not promotion_result.get('premium_products'):
					continue
				for premium_product in promotion_result['premium_products']:
					premium_order_product = OrderProduct(self.context['webapp_owner'], self.context['webapp_user'])
					premium_order_product.name = premium_product['name']
					if promotion_result_version == settings.PROMOTION_RESULT_VERSION:
						premium_order_product.purchase_count = premium_product['premium_count']
						premium_order_product.thumbnails_url = '%s%s' % (settings.IMAGE_HOST, premium_product['thumbnails_url']) if premium_product['thumbnails_url'].find('http') == -1 else premium_product['thumbnails_url']
					else:
						premium_order_product.purchase_count = premium_product['count']
						premium_order_product.thumbnails_url = '%s%s' % (settings.IMAGE_HOST, premium_product['thumbnails_url']) if premium_product['thumbnails_url'].find('http') == -1 else premium_product['thumbnails_url']
					premium_order_product.id = premium_product['id']
					premium_order_product.price = 0	
					premium_order_product.promotion = {
						'type_name': 'premium_sale:premium_product'
					}
					premium_order_product.supplier = premium_product.get('supplier', None)

					self.products.append(premium_order_product)
