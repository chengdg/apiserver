# -*- coding: utf-8 -*-
"""@package business.inegral_allocator.IntegralResourceAllocator
请求积分资源

"""
import logging
import json
from bs4 import BeautifulSoup
import math
import itertools
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from eaglet.core import watchdog
from business import model as business_model
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.mall.realtime_stock import RealtimeStock
from core.decorator import deprecated
from business.resource.product_resource_checker import ProductResourceChecker

class ProductResource(business_model.Resource):
	"""商品资源
	"""
	__slots__ = (
		'type',
		'model_id',
		'purchase_count'
		)


	@staticmethod
	@param_required(['type'])
	def get(args):
		"""工厂方法，创建ProductResourcee对象

		@return ProductResource对象
		"""
		product_resource = ProductResource(args['type'])

		return product_resource

	def __init__(self, type):
		business_model.Resource.__init__(self)
		self.type = type
		self.model_id = 0
		self.purchase_count = 0

	def get_type(self):
		return self.type

	@deprecated
	def get_resources(self, product, purchase_info):
		"""
		@todo 需要将这段代码迁移到ProductResourceAllocator中
		"""

		product_resource_checker = ProductResourceChecker()
		is_succeeded, reason = product_resource_checker.check(product)
		if not is_succeeded:
			logging.info("reason in `ProductResource.get_resources(): {}".format(reason))
			return False, reason
		# purchase_info.lock wapi锁,根据它判断是否是openapi发起的下单，如果lock为False就不校验了.lock为False代表未被wapi锁，说明是openapi的下单
		if product.limit_zone_type and purchase_info.lock:
			is_succeeded, reason = self.checkout_sale_zone(product, purchase_info)
			if not is_succeeded:
				logging.info("reason in `ProductResource.get_resources(): {}".format(reason))
				return False, reason
		is_succeeded, reason = self.consume_stocks(product)
		if not is_succeeded:
			logging.info("reason in `ProductResource.get_resources(): {}".format(reason))
			return False, reason

		return True, reason

	def consume_stocks(self, product):
		"""
		消耗库存
		@note 库存的并发防超售（防止有限库存在并发时库存被扣为负数）依赖MySQL的unsigned int，而MySQL对于修改为负数的SQL不会报错，而pymsql和MySQLdb会抛出异常，以此异常为“扣为负数”的判断。
		@todo redis接管库存
		"""
		#请求分配库存资源
		realtime_stock = RealtimeStock.from_product_model_name({
				'model_name': product.model_name,
				'product_id': product.id
			})
		model2stock = realtime_stock.model2stock
		if not model2stock and len(model2stock) != 1:
			return False, {
				'is_successed': False,
				'type': 'product:is_deleted',
				'msg': u'商品已删除',
				'short_msg': u'商品已删除'
			}

		current_model_id = model2stock.keys()[0]
		current_model = model2stock[current_model_id]

		if current_model['stock_type'] == mall_models.PRODUCT_STOCK_TYPE_LIMIT:
			if product.purchase_count > current_model['stocks']:
				if current_model['stocks'] == 0:
					return False, {
						'is_successed': False,
						'type': 'product:sellout',
						'msg': u'商品已售罄',
						'short_msg': u'商品已售罄'
					}
				else:
					return False, {
						'is_successed': False,
						'type': 'product:not_enough_stocks',
						'msg': u'',
						'short_msg': u'库存不足'
					}

			# stocks字段类型为unsigned int
			try:
				mall_models.ProductModel.update(stocks=mall_models.ProductModel.stocks-product.purchase_count).dj_where(id=current_model_id).execute()
			except:
				return False, {
					'is_successed': False,
					'type': 'product:sellout',
					'msg': u'商品已售罄',
					'short_msg': u'商品已售罄'
				}
		self.purchase_count = product.purchase_count
		self.model_id = current_model_id
		return True, {
			'is_successed': True,
			'count': product.purchase_count
		}

	def checkout_sale_zone(self, product, purchase_info):
		"""
		校验商品是否在销售区域
		"""
		area = purchase_info.ship_info['area']
		user_province_id = area.split('_')[0]
		user_city_id = area.split('_')[1]
		limit_zone_type = product.limit_zone_type
		limit_zone_template = mall_models.ProductLimitZoneTemplate.select().dj_where(id=product.limit_zone).first()
		limit_provinces = limit_zone_template.provinces
		limit_cities = limit_zone_template.cities
		cities = mall_models.City.select().dj_where(id__in=limit_cities.split(',')) if limit_cities else []

		# 构建省id和对应城市id的字典，如果对应是空说明整个省市都有限制
		province_id2city_ids = {}
		for city in cities:
			if str(city.province_id) in province_id2city_ids:
				province_id2city_ids[str(city.province_id)].append(str(city.id))
			else:
				province_id2city_ids[str(city.province_id)] = [str(city.id)]
		for province_id in limit_provinces.split(','):
			if province_id not in province_id2city_ids:
				province_id2city_ids[province_id] = []

		if limit_zone_type == 1:
			if user_province_id in province_id2city_ids and (not province_id2city_ids[user_province_id] or user_city_id in province_id2city_ids[user_province_id]):
				return False, {
					'is_successed': False,
					'type': 'product:out_limit_zone',
					'msg': u'该订单内商品状态发生变化',
					'short_msg': u'超出范围'
				}
		elif limit_zone_type == 2:
			if user_province_id not in province_id2city_ids or (province_id2city_ids[user_province_id] and user_city_id not in province_id2city_ids[user_province_id]):
				return False, {
					'is_successed': False,
					'type': 'product:out_limit_zone',
					'msg': u'该订单内商品状态发生变化',
					'short_msg': u'超出范围'
				}
		return True, {
			'is_successed': True
		}
		# flag = False
		# if limit_zone_type == 1:
		# 	if limit_zone_template.cities:
		# 		#  有城市
		# 		city_of_province_ids = [str(model.province_id) for model in mall_models.City.select().dj_where(id__in=limit_cities.split(','))]
		# 		if user_city_id in limit_cities.split(','):
		# 			flag = True
		# 		else:
		# 			if province_id not in ['1', '2', '9', '22', '32', '33', '34']:
		# 				# 排除直辖市和其他
		# 				if province_id not in city_of_province_ids:
		# 					# 全选
		# 					if province_id in limit_provinces.split(','):
		# 						flag = True
		# 			else:
		# 				if province_id in limit_provinces.split(','):
		# 					flag = True
		# 	else:
		# 		# 全部是全选，判断省
		# 		if province_id in limit_provinces.split(','):
		# 			flag = True
		# elif limit_zone_type == 2:
		# 	if limit_zone_template.cities:
		# 		city_of_province_ids = [str(model.province_id) for model in mall_models.City.select().dj_where(id__in=limit_cities.split(','))]
		# 		if province_id in city_of_province_ids:
		# 			# 仅售单个城市
		# 			if user_city_id not in limit_cities.split(','):
		# 				flag = True
		# 		else:
		# 			# 城市被全选
		# 			if province_id not in limit_provinces.split(','):
		# 				flag = True
		# 	else:
		# 		if province_id not in limit_provinces.split(','):
		# 			flag = True


		# if flag:
		# 	return False, {
		# 			'is_successed': False,
		# 			'type': 'product:out_limit_zone',
		# 			'msg': u'该订单内商品状态发生变化',
		# 			'short_msg': u'超出范围'
		# 		}
		# else:
		# 	return True, {
		# 		'is_successed': True
		# 	}
