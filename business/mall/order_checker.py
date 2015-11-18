# -*- coding: utf-8 -*-

"""订单有效性的判断器
"""

import json
from bs4 import BeautifulSoup
import math

from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
import resource
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
				for detail in data['data']['detail']:
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
				'reason': self.__create_failed_reason(failed_results)
			}
		else:
			return {'is_valid': True}