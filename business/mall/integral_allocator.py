# -*- coding: utf-8 -*-
"""@package business.inegral_allocator.IntegralAllocator
请求积分资源

"""
import logging
import json
from bs4 import BeautifulSoup
import math
import itertools
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from utils import allocator_type 


class IntegralAllocator(business_model.Model):
	"""下单使用积分
	"""
	__slots__ = (
		'order',
		'result'
		)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user


	def release(self, resources):
		#TODO-bert
		for_release = []
		for resource in resources:
			if resource['type'] == allocator_type.ALLOCATOR_INTEGRAL:
				for_release.append(resource['release'])

		for release_data in for_release:
			#TODO-bert 积分返回，积分日志删除
			pass

	def allocated_integral(self, order, purchase_info):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		count_per_yuan = webapp_owner.integral_strategy_settings.integral_each_yuan
		total_integral = 0
		if purchase_info.purchase_integral_info:
			use_ceiling = webapp_owner.integral_strategy_settings.use_ceiling
			if use_ceiling < 0:
				return False, u'积分抵扣尚未开启', None

			total_integral = purchase_info.purchase_integral_info['integral']
			integral_money = round(float(purchase_info.purchase_integral_info['money']), 2)
			product_price = sum([product.price * product.purchase_count for product in products])
			if (integral_money - 1) > round(product_price * use_ceiling / 100, 2)\
				or (total_integral + 1) < (integral_money * count_per_yuan):
				return False, u'积分使用超限', None

		elif purchase_info.purchase_group2integral_info:
			fail_msg = ''

			data_detail = []
			purchase_group2integral_info =  purchase_info.purchase_group2integral_info
			group2integral_sale_rule = dict((group['uid'], group['integral_sale_rule']) for group in product_groups)
			uid2group = dict((group['uid'], group) for group in product_groups)
			for group_uid, integral_info in purchase_group2integral_info.items():
				products = uid2group[group_uid]['products']
				if not group_uid in group2integral_sale_rule.keys() or not group2integral_sale_rule[group_uid]:
					for product in products:
						fail_msg = u'积分折扣已经过期'
						break
				if fail_msg:
					break

				use_integral = int(integral_info['integral'])
				# integral_info['money'] = integral_info['money'] *
				integral_money = round(float(integral_info['money']), 2) #round(1.0 * use_integral / count_per_yuan, 2)
				
				# 校验前台输入：积分金额不能大于使用上限、积分值不能小于积分金额对应积分值
				# 根据用户会员与否返回对应的商品价格
				product_price = sum([product.price * product.purchase_count for product in products])
				integral_sale_rule = group2integral_sale_rule[group_uid]
				max_integral_price = round(product_price * integral_sale_rule['rule']['discount'] / 100, 2)
				if max_integral_price < (integral_money - 0.01) \
					or (integral_money * count_per_yuan) > (use_integral + 1):
					for product in products:
						fail_msg = u'使用积分不能大于促销限额'
						break
				if fail_msg:
					break

				integral_sale_rule = group2integral_sale_rule[group_uid]
				integral_sale_rule['result'] = {
					'final_saved_money': integral_money,
					'promotion_saved_money': integral_money,
					'use_integral': use_integral
				}
				total_integral += use_integral

			if fail_msg:
				return False, fail_msg, None


		if total_integral > 0 and not webapp_user.can_use_integral(total_integral):
			return {
					'success': False,
					'data': {
						'msg': u'积分不足',
					}
				}
		elif total_integral == 0:
			return True, '', {
				'type': allocator_type.ALLOCATOR_INTEGRAL,
				'integral': 0,
				'integral_money': 0,
				'release': {
					'integral': 0,
					'integral_log_id': None
				}
			}
			
		else:
			logging.error(total_integral)
			successed, integral_log_id = webapp_user.use_integral(total_integral)
			#TODO-bert 使用积分异常
			if not successed:
				return False, u'使用积分异常', {
					'type': allocator_type.ALLOCATOR_INTEGRAL,
					'integral': total_integral,
					'integral_money': integral_money,
					'release': {
						'integral': total_integral,
						'integral_log_id': integral_log_id
					}
				}

			return True, '', {
				'type': allocator_type.ALLOCATOR_INTEGRAL,
				'integral': total_integral,
				'integral_money': integral_money,
				'release': {
					'integral': total_integral,
					'integral_log_id': integral_log_id
				}
			}