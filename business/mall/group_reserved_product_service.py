# -*- coding: utf-8 -*-
"""@package business.mall.group_reserved_product_service
商品分组器，根据促销信息对商品进行分组

"""

import json
from bs4 import BeautifulSoup
import math
import itertools
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
#import resource
from eaglet.core import watchdog
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.mall.order_products import OrderProducts
from business.mall.promotion_product_group import PromotionProductGroup


class GroupReservedProductService(business_model.Service):
	"""商品分组器
	"""
	__slots__ = (
		#'product_groups',
	)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self, webapp_owner, webapp_user)

	def __get_promotion_name(self, product):
		"""
		为product生成一个包含promotion信息的name

		Parameters
			[in] product: 商品

		Returns
			包含promotion信息的name
		"""
		name = 'no_promotion'
		promotion = product.promotion
		if not promotion:
			promotion = product.integral_sale
			
		if promotion:
			# 已过期或未开始活动的商品，做为 普通商品
			if promotion.type == promotion_models.PROMOTION_TYPE_PRICE_CUT or promotion.type == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
				name = promotion.id
			else:
				name = '%d_%s' % (promotion.id, product.model.name)
		'''
		elif hasattr(product, 'integral_sale'):
			return '%d_%s' % (product.integral_sale['id'], product.model['name'])
		'''

		return name

	def __get_group_name(self, group_products):
		"""
		获取商品分组名

		Parameters
			[in] group_products: 分组中的商品集合

		Returns
			生成的分组名，格式为"id1_modelname1-id2_modelname2..."
		"""
		items = []
		for product in group_products:
			items.append('%s_%s' % (product.id, product.model.name))

		return '-'.join(items)

	# def __collect_integral_sale_rules(self, target_member_grade_id, products):
	# 	"""
	# 	收集product_group积分规则抵扣规则
	# 	"""
	# 	return None
	# 	merged_rule = {
	# 		"member_grade_id": target_member_grade_id,
	# 		"product_model_names": []
	# 	}
	# 	for product in products:
	# 		product.active_integral_sale_rule = None
	# 		product_model_name = '%s_%s' % (product.id, product.model['name'])
	# 		#判断积分应用是否不可用
	# 		if not product.integral_sale_model:
	# 			continue
	# 		if not product.integral_sale_model.is_active:
	# 			if product.integral_sale['detail']['is_permanant_active']:
	# 				pass
	# 			else:
	# 				continue

	# 		for rule in product.integral_sale['detail']['rules']:
	# 			member_grade_id = int(rule['member_grade_id'])
	# 			if member_grade_id <= 0 or member_grade_id == target_member_grade_id:
	# 				# member_grade_id == -1则为全部会员等级
	# 				merged_rule['product_model_names'].append(product_model_name)
	# 				product.active_integral_sale_rule = rule
	# 				merged_rule['rule'] = rule
	# 		merged_rule['integral_product_info'] = str(product.id) + '-' + product.model_name
	# 	if len(merged_rule['product_model_names']) > 0:
	# 		return merged_rule
	# 	else:
	# 		return None

	def group_product_by_promotion(self, products):
		"""
		根据商品促销类型对商品进行分类

		Parameters
			[in] member: Member业务对象
			[in] products: 待分组的商品集合

		Returns
			PromotionProductGroup业务对象的list
		"""
		member = self.context['webapp_user'].member
		member_grade_id, discount = member.discount
		#按照促销对product进行聚类, 生成<product_promotion_name, <product, product, ...]>映射
		product_groups = []
		promotion2products = {}
		group_id = 0
		for product in products:
			#对于满减，同一活动中不同规格的商品不能分开，其他活动，需要分开
			group_id += 1
			default_products = {"group_id": group_id, "products": []}
			promotion_name = self.__get_promotion_name(product)
			promotion2products.setdefault(promotion_name, default_products)['products'].append(product)

		items = promotion2products.items()
		items.sort(lambda x, y: cmp(x[1]['group_id'], y[1]['group_id']))
		for product_promotion_name, group_info in items:
			products = group_info['products']
			group_id = group_info['group_id']
			group_unified_id = self.__get_group_name(products)

			#products是相同promotion的集合，所以从第一个product中获取promotion就能得到promotion对象了
			promotion = products[0].promotion
			integral_sale = products[0].integral_sale

			# 商品没有参加促销，
			if not promotion:
				promotion_product_group = PromotionProductGroup({
					"id": group_id,
					"uid": group_unified_id,
					'products': products,
					'promotion': None,
					'integral_sale': integral_sale,
					"promotion_type": '',
					'member_grade_id': member_grade_id
				})
				product_groups.append(promotion_product_group)
				continue

			promotion_type = promotion.type
			if promotion_type == 0:
				type_name = 'none'
			else:
				type_name = promotion.type_name

			'''
			if promotion_type == promotion_models.PROMOTION_TYPE_FLASH_SALE:
				product = products[0]
				promotion_price = product.promotion.detail.get('promotion_price', 0)
				product.price = promotion_price
				#TODO2: 会员价不和限时抢购叠加
				#product.member_discount_money = 0
				promotion_result = {
					"saved_money": product.original_price - promotion_price,
					"subtotal": product.purchase_count * product.price
				}

				can_use_promotion = (promotion.status == promotion_models.PROMOTION_STATUS_STARTED)
			# 买赠
			elif promotion_type == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
				first_product = products[0]
				promotion = first_product.promotion
				promotion_detail = promotion.detail
				can_use_promotion = (promotion.status == promotion_models.PROMOTION_STATUS_STARTED)

				total_purchase_count = 0
				total_product_price = 0.0
				for product in products:
					total_purchase_count += product.purchase_count
					total_product_price += product.price * product.purchase_count

				if total_purchase_count < promotion_detail['count']:
					can_use_promotion = False
				else:
					#如果满足循环满赠，则调整赠品数量
					for product in products:
						product.price = product.original_price
					if promotion_detail['is_enable_cycle_mode']:
						premium_round_count = total_purchase_count / promotion.detail['count']
						for premium_product in promotion_detail['premium_products']:
							premium_product['original_premium_count'] = premium_product['premium_count']
							premium_product['premium_count'] = premium_product['premium_count'] * premium_round_count
				promotion_result = {
					"subtotal": product.purchase_count * product.price
				}
			# 满减
			elif promotion_type == promotion_models.PROMOTION_TYPE_PRICE_CUT:
				promotion = products[0].promotion
				promotion_detail = promotion.detail
				total_price = 0.0
				for product in products:
					total_price += product.price * product.purchase_count
				can_use_promotion = (total_price - promotion_detail['price_threshold']) >= 0
				promotion_round_count = 1  # 循环满减执行的次数
				if promotion_detail['is_enable_cycle_mode']:
					promotion_round_count = int(total_price / promotion_detail['price_threshold'])
				if can_use_promotion:
					subtotal = total_price - promotion_detail['cut_money']*promotion_round_count
				else:
					subtotal = total_price
				promotion_result = {
					"subtotal": subtotal,
					"price_threshold": promotion_round_count*promotion_detail['price_threshold']
				}
			'''

			promotion_product_group = PromotionProductGroup({
				"id": group_id,
				"uid": group_unified_id,
				"promotion_type": promotion.type_name,
				'products': products,
				'promotion': promotion,
				'integral_sale': integral_sale,
				'member_grade_id': member_grade_id
			})
			product_groups.append(promotion_product_group)

		#self.product_groups = product_groups
		return product_groups



