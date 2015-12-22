# -*- coding: utf-8 -*-
"""@package business.mall.order_checker
订单有效性的判断器

在下单过程中，对待生成的订单进行一系列的检查，比如检查是否购买的商品已下家、检查会员当前的积分是否足以抵扣订单中的积分等等

通常，我们通过以下的方式使用OrderChecker
```python
order_checker = OrderChecker(webapp_owner, webapp_user, order)
check_result = order_checker.check()

if check_result['is_valid']:
	#订单通过检查，继续下单流程
	...
else:
	#订单没有通过检查，返回失败原因
	return check_result['reason']
```

"""

import json
from bs4 import BeautifulSoup
import math

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 


class OrderChecker(business_model.Model):
	"""
	订单有效性的判断器
	"""
	__slots__ = ('order',)

	def __init__(self, webapp_owner, webapp_user, order):
		business_model.Model.__init__(self)

		self.context['checkers'] = [
			self.__check_products, 
			self.__check_coupon,
			self.__check_product_stock
		]

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user
		self.order = order


	def __check_products(self):
		"""
		检查是否有商品下架
		"""
		webapp_owner_id = self.context['webapp_owner'].id
		products = self.order.products
		off_shelve_products = [product for product in products if not product.is_on_shelve()]
		if len(off_shelve_products) > 0:
			if len(off_shelve_products) == len(products):
				#所有商品下架，返回商品列表页
				return {
					'success': False,
					'data': {
						'msg': u'商品已下架<br/>2秒后返回商城首页',
						'redirect_url': '/workbench/jqm/preview/?module=mall&model=products&action=list&category_id=0&workspace_id=mall&woid=%s' % webapp_owner_id
					}
				}
			else:
				return {
					'success': False,
					'data': {
						'msg': u'有商品已下架<br/>2秒后返回购物车<br/>请重新下单',
						'redirect_url': '/workbench/jqm/preview/?module=mall&model=shopping_cart&action=show&workspace_id=mall&woid=%s' % webapp_owner_id
					}
				}
		else:
			return {
				'success': True
			}

	def __check_coupon(self):
		"""
		检查优惠券
		"""
		return {
			'success': True
		}
		'''
		if not hasattr(self, 'session_data'):
			self.session_data = dict()
		fail_msg = {
			'success': False,
			'data': {
				'msg': u'',
				'redirect_url': 'http://h5.weapp.com/mall/shopping_cart/?woid=%s' % webapp_owner_id
			}
		}
		is_use_coupon = (request_args.get('is_use_coupon', 'false') == 'true')
		if is_use_coupon:
			coupon_id = request_args.get('coupon_id', 0)
			#modified by duhao 20150909
			# product_prices = [product.price * product.purchase_count for product in pre_order.products]
			# product_ids = [str(product.id) for product in pre_order.products]
			product_prices = []
			product_ids = []
			product_id2price = {}
			for product in self.products:
				price = product.price * product.purchase_count
				product_ids.append(str(product.id))
				product_prices.append(price)
				if not product_id2price.has_key(product.id):
					#用于处理同一商品买了不同规格的情况
					product_id2price[product.id] = 0.0

				product_id2price[product.id] += price

			from market_tools.tools.coupon import util as coupon_util
			msg, coupon = coupon_util.has_can_use_by_coupon_id(coupon_id, request.webapp_owner_id, product_prices, product_ids, request.member.id, products=pre_order.products, product_id2price=product_id2price)
			if coupon:
				self.session_data['coupon'] = coupon
			else:
				fail_msg['data']['msg'] = msg
				return fail_msg
		return {
			'success': True
		}
		'''

	def __fill_realtime_stocks(self, products):
		"""
		填充实时库存
		"""
		models = []
		for product in products:
			if product.is_use_custom_model:
				for model in product.models[1:]:
					model['product_id'] = product.id
					models.append(model)
			else:
				model = product.models[0]
				model['product_id'] = product.id
				models.append(model)

		model_ids = [model['id'] for model in models]
		db_product_models = mall_models.ProductModel.select().dj_where(id__in=model_ids)
		id2productmodels = dict([('%s_%s' % (model.product_id, model.id), model) for model in db_product_models])
		for product in products:
			if product.is_use_custom_model:
				for model in product.models[1:]:
					realtime_model = id2productmodels['%s_%s' % (product.id, model['id'])]
					model['stock_type'] = realtime_model['stock_type']
					model['stocks'] = realtime_model['stocks']
					model['is_deleted'] = realtime_model['is_deleted']
			else:
				model = product.models[0]
				realtime_model = id2productmodels['%s_%s' % (product.id, model['id'])]
				model['stock_type'] = realtime_model['stock_type']
				model['stocks'] = realtime_model['stocks']
				model['is_deleted'] = realtime_model['is_deleted']

	def __check_product_stock(self):
		"""
		检查商品库存是否满足下单条件
		@todo 改为基于redis的并发安全的实现
		"""
		webapp_owner_id = self.context['webapp_owner'].id
		fail_msg = {
			'success': False,
			'data': {
				'msg': u'有商品库存不足<br/>2秒后返回购物车<br/>请重新下单',
				'redirect_url': '/workbench/jqm/preview/?module=mall&model=shopping_cart&action=show&workspace_id=mall&woid=%s' % webapp_owner_id,
				'detail': []
			}
		}

		products = self.order.products
		for product in products:
			stock_result = product.check_stocks()
			if not stock_result["is_sufficient"]:
				reason = stock_result["reason"]
				if reason == 'deleted':
					fail_msg['data']['detail'].append({
							'id': product.id,
							'model_name': product.model_name,
							'msg': u'有商品规格已删除，请重新下单',
							'short_msg': u'已删除'
						})
				elif reason == 'sellout':
					fail_msg['data']['detail'].append({
						'id': product.id,
						'model_name': product.model_name,
						'msg': u'有商品已售罄，请重新下单',
						'short_msg': u'已售罄'
					})
				else:
					fail_msg['data']['detail'].append({
						'id': product.id,
						'model_name': product.model_name,
						'msg': u'有商品库存不足，请重新下单',
						'short_msg': u'库存不足'
					})

		if len(fail_msg['data']['detail']) > 0:
			return fail_msg

		return {
			'success': True
		}

	def __check_pro_id_in_detail_list(self, datadetail, pro_id):
		flag, index = False,0
		for index, data in enumerate (datadetail):
			if data['id'] == pro_id and data['short_msg'] == u'已删除':
				flag, index = True, index # 存在，以及索引
				break
			elif data['id'] == pro_id and data['short_msg'] == u'已下架':
				flag, index = True, index # 存在，以及索引
			else:
				flag, index = False, index # 存在，以及索引
		return flag,index

	def __create_failed_reason(self, failed_results):
		details = []
		real_details = []
		for failed_result in failed_results:
			if failed_result['data'].has_key('detail'):
				for detail in failed_result['data']['detail']:
					details.append(detail)

		products_ids = [detail['id'] for detail in details]
		for id in products_ids:
			flag, index = self.__check_pro_id_in_detail_list(details,id)
			if flag:
				real_details.append(details[index])
				continue
			else:
				for detail in details:
					if detail['id'] == id:
						real_details.append(detail)
		
		return real_details

	def check(self):
		"""
		检查order的有效性

		@return
			is_valid: 是否有效
			reason: 当is_valid为False时，失效的理由
		"""
		failed_results = []
		for checker in self.context['checkers']:
			result = checker()
			if not result['success']:
				failed_results.append(result)

		if len(failed_results) > 0:
			return {
				'is_valid': False,
				'reason': {
					'detail': self.__create_failed_reason(failed_results)
				}
			}
		else:
			return {'is_valid': True}


	# def __check_integral(self):
	# 	webapp_owner = self.context['webapp_owner']
	# 	webapp_user = self.context['webapp_user']

	# 	count_per_yuan = webapp_owner.integral_strategy_settings.integral_each_yuan

	# 	if self.order.purchase_integral_info:
	# 		use_ceiling = webapp_owner.integral_strategy_settings.use_ceiling
	# 		if use_ceiling < 0:
	# 			return {
	# 				'success': False,
	# 				'data': {
	# 					'msg': u'积分抵扣尚未开启',
	# 				}
	# 			}

	# 		total_integral = self.order.purchase_integral_info['integral']
	# 		integral_money = round(float(self.order.purchase_integral_info['money']), 2)
	# 		product_price = sum([product.price * product.purchase_count for product in self.order.products])
	# 		if (integral_money - 1) > round(product_price * use_ceiling / 100, 2)\
	# 			or (total_integral + 1) < (integral_money * count_per_yuan):
	# 			return {
	# 				'success': False,
	# 				'data': {
	# 					'msg': u'积分使用超限',
	# 				}
	# 			}

	# 	elif self.order.purchase_group2integral_info:
	# 		fail_msg = {
	# 			'success': False,
	# 			'data': {
	# 				'msg': u'有商品库存不足<br/>2秒后返回购物车<br/>请重新下单',
	# 				'redirect_url': '/workbench/jqm/preview/?module=mall&model=shopping_cart&action=show&workspace_id=mall&woid=%s' % webapp_owner_id,
	# 				'detail': []
	# 			}
	# 		}

	# 		data_detail = []
	# 		purchase_group2integral_info =  self.order.purchase_group2integral_info
	# 		group2integral_sale_rule = dict((group['uid'], group['integral_sale_rule']) for group in self.order.product_groups)
	# 		uid2group = dict((group['uid'], group) for group in product_groups)
	# 		for group_uid, integral_info in purchase_group2integral_info.items():
	# 			products = uid2group[group_uid]['products']
	# 			if not group_uid in group2integral_sale_rule.keys() or not group2integral_sale_rule[group_uid]:
	# 				for product in products:
	# 					fail_msg['data']['detail'].append({
	# 						'id': product.id,
	# 						'model_name': product.model_name,
	# 						'msg': '积分折扣已经过期',
	# 						'short_msg': '已经过期'
	# 					})
	# 				continue
	# 			use_integral = int(integral_info['integral'])
	# 			# integral_info['money'] = integral_info['money'] *
	# 			integral_money = round(float(integral_info['money']), 2) #round(1.0 * use_integral / count_per_yuan, 2)
				
	# 			# 校验前台输入：积分金额不能大于使用上限、积分值不能小于积分金额对应积分值
	# 			# 根据用户会员与否返回对应的商品价格
	# 			product_price = sum([product.price * product.purchase_count for product in products])
	# 			integral_sale_rule = group2integral_sale_rule[group_uid]
	# 			max_integral_price = round(product_price * integral_sale_rule['rule']['discount'] / 100, 2)
	# 			if max_integral_price < (integral_money - 0.01) \
	# 				or (integral_money * count_per_yuan) > (use_integral + 1):
	# 				for product in products:
	# 					fail_msg['data']['detail'].append({
	# 							'id': product.id,
	# 							'model_name': product.model_name,
	# 							'msg': '使用积分不能大于促销限额',
	# 							'short_msg': '积分应用',
	# 						})
	# 			integral_sale_rule = group2integral_sale_rule[group_uid]
	# 			integral_sale_rule['result'] = {
	# 				'final_saved_money': integral_money,
	# 				'promotion_saved_money': integral_money,
	# 				'use_integral': use_integral
	# 			}
	# 			total_integral += use_integral

	# 		if len(fail_msg['data']['detail']) > 0:
	# 			return fail_msg


	# 	if total_integral > 0 and not webapp_user.can_use_integral(total_integral):
	# 		return {
	# 				'success': False,
	# 				'data': {
	# 					'msg': u'积分不足',
	# 				}
	# 			}
	# 	return {
	# 		'success': True
	# 	}