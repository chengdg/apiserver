# -*- coding: utf-8 -*-

"""商品分组器

"""

import json
from bs4 import BeautifulSoup
import math
import itertools

from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
from wapi.mall import promotion_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.mall.order_products import OrderProducts


class ProductGrouper(business_model.Model):
	"""商品分组器
	"""
	__slots__ = ()

	def __get_promotion_name(self, product):
		"""
		mall_api:__get_promotion_name
		判断商品是否促销， 没有返回None, 有返回促销ID与商品的规格名.

		Args:
		  product -

		Return:
		  None - 商品没有促销
		  'int_str' - 商品有促销
		"""
		name = None
		if product.promotion:
			promotion = product.promotion
			now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
			# 已过期或未开始活动的商品，做为 普通商品
			if promotion['start_date'] > now or promotion['end_date'] < now:
				name = '%d_%s' % (promotion['id'], product.model['name'])
			elif promotion['type'] == promotion_models.PROMOTION_TYPE_PRICE_CUT or promotion['type'] == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
				name = promotion['id']
			else:
				name = '%d_%s' % (promotion['id'], product.model['name'])
		elif hasattr(product, 'integral_sale'):
			return '%d_%s' % (product.integral_sale['id'], product.model['name'])

		return name

	def __get_group_name(self, group_products):
		items = []
		for product in group_products:
			items.append('%s_%s' % (product.id, product.model['name']))
		return '-'.join(items)

	def __collect_integral_sale_rules(self, target_member_grade_id, products):
		"""
		收集product_group积分规则抵扣规则
		"""
		merged_rule = {
			"member_grade_id": target_member_grade_id,
			"product_model_names": []
		}
		for product in products:
			product.active_integral_sale_rule = None
			product_model_name = '%s_%s' % (product.id, product.model['name'])
			#判断积分应用是否不可用
			if not product.integral_sale_model:
				continue
			if not product.integral_sale_model.is_active:
				if product.integral_sale['detail']['is_permanant_active']:
					pass
				else:
					continue

			for rule in product.integral_sale['detail']['rules']:
				member_grade_id = int(rule['member_grade_id'])
				if member_grade_id <= 0 or member_grade_id == target_member_grade_id:
					# member_grade_id == -1则为全部会员等级
					merged_rule['product_model_names'].append(product_model_name)
					product.active_integral_sale_rule = rule
					merged_rule['rule'] = rule
			merged_rule['integral_product_info'] = str(product.id) + '-' + product.model_name
		if len(merged_rule['product_model_names']) > 0:
			return merged_rule
		else:
			return None

	def __has_promotion(self, user_member_grade_id=None, promotion_member_grade_id=0):
		"""判断促销是否对用户开放.

		Args:
			user_member_grade_id(int): 用户会员等价
			promotion_member_grade_id(int): 促销制定的会员等级

		Return:
			True - if 促销对用户开放
			False - if 促销不对用户开放
		"""
		if promotion_member_grade_id <= 0:
			return True
		elif promotion_member_grade_id == user_member_grade_id:
			return True
		else:
			return False

	def group_product_by_promotion(self, member, products):
		"""
		mall_api:group_product_by_promotion
		根据商品促销类型对商品进行分类
		Args:
		  products -

		Return:
		  list - [
					  {'id': ,
					   'uid': ,
					   'products':,
					   'promotion':,
					   'promotion_type': (str),
					   'promotion_result':,
					   'integral_sale_rule':,
					   'can_use_promotion':,
					   'member_grade_id': }
					  ...
				   ]
		"""
		member_grade_id = member.grade_id
		#按照促销对product进行聚类
		# global NO_PROMOTION_ID
		# NO_PROMOTION_ID = -1  # 负数的promotion id表示商品没有promotion
		product_groups = []
		promotion2products = {}
		group_id = 0
		for product in products:
			product.original_price = product.price
			if product.is_member_product:
				product.price = round(product.price * member.discount / 100, 2)
			#对于满减，同一活动中不同规格的商品不能分开，其他活动，需要分开
			group_id += 1
			default_products = {"group_id": group_id, "products": []}
			promotion_name = self.__get_promotion_name(product)
			promotion2products.setdefault(promotion_name, default_products)['products'].append(product)
		now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		items = promotion2products.items()
		items.sort(lambda x, y: cmp(x[1]['group_id'], y[1]['group_id']))
		for promotion_id, group_info in items:
			products = group_info['products']
			group_id = group_info['group_id']
			group_unified_id = self.__get_group_name(products)
			integral_sale_rule = self.__collect_integral_sale_rules(member_grade_id, products) if member_grade_id != -1 else None

			promotion = products[0].promotion
			# 商品没有参加促销
			if not promotion or promotion_id <= 0:
				product_groups.append({
					"id": group_id,
					"uid": group_unified_id,
					'products': products,
					'promotion': {},
					"promotion_type": '',
					'promotion_result': '',
					'integral_sale_rule': integral_sale_rule,
					'can_use_promotion': False,
					'member_grade_id': member_grade_id
				})
				continue


			# 如果促销对此会员等级的用户不开放
			if not self.__has_promotion(member_grade_id, promotion.get('member_grade_id')):
				product_groups.append({
									  "id": group_id,
									  "uid": group_unified_id,
									  'products': products,
									  'promotion': {},
									  "promotion_type": '',
									  'promotion_result': '',
									  'integral_sale_rule': integral_sale_rule,
									  'can_use_promotion': False,
									  'member_grade_id': member_grade_id
									  })
				continue
			promotion_type = promotion.get('type', 0)
			if promotion_type == 0:
				type_name = 'none'
			else:
				type_name = promotion_models.PROMOTION2TYPE[promotion_type]['name']

			promotion_result = None
			can_use_promotion = False
			# #判断promotion状态
			# 促销活动还未开始，或已结束
			if promotion['start_date'] > now or promotion['end_date'] < now:
				promotion['status'] = promotion_models.PROMOTION_STATUS_NOT_START if promotion['start_date'] > now else promotion_models.PROMOTION_STATUS_FINISHED
			# 限时抢购
			elif promotion_type == promotion_models.PROMOTION_TYPE_FLASH_SALE:
				product = products[0]
				promotion_price = product.promotion['detail'].get('promotion_price', 0)
				product.price = promotion_price
				# 会员价不和限时抢购叠加
				product.member_discount_money = 0
				promotion_result = {
					"saved_money": product.original_price - promotion_price,
					"subtotal": product.purchase_count * product.price
				}

				can_use_promotion = (promotion['status'] == promotion_models.PROMOTION_STATUS_STARTED)
			# 买赠
			elif promotion_type == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
				first_product = products[0]
				promotion = first_product.promotion
				promotion_detail = promotion['detail']
				can_use_promotion = (promotion['status'] == promotion_models.PROMOTION_STATUS_STARTED)

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
						premium_round_count = total_purchase_count / promotion['detail']['count']
						for premium_product in promotion_detail['premium_products']:
							premium_product['original_premium_count'] = premium_product['premium_count']
							premium_product['premium_count'] = premium_product['premium_count'] * premium_round_count
				promotion_result = {
					"subtotal": product.purchase_count * product.price
				}
			# 满减
			elif promotion_type == promotion_models.PROMOTION_TYPE_PRICE_CUT:
				promotion = products[0].promotion
				promotion_detail = promotion['detail']
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
			product_groups.append({
				"id": group_id,
				"uid": group_unified_id,
				"promotion_type": type_name,
				'products': products,
				'promotion': promotion,
				'promotion_result': promotion_result,
				'integral_sale_rule': integral_sale_rule,
				'can_use_promotion': can_use_promotion,
				'promotion_json': json.dumps(promotion),
				'member_grade_id': member_grade_id
			})
		return product_groups
