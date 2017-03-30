# -*- coding: utf-8 -*-
"""@package business.mall.simple_products
携带基础商品信息的商品集合，用于商品列表页面的展示
"""

import json
from bs4 import BeautifulSoup
import math
import itertools
from operator import attrgetter
import pickle

from eaglet.decorator import param_required
#from wapi import wapi_utils
from bdem import msgutil
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from eaglet.core import watchdog
from eaglet.core import paginator
from business import model as business_model 
import settings
from business.mall.product import Product
from util import redis_util


class NewSimpleProducts(business_model.Model):
	"""
	携带基础商品信息的商品集合
	"""
	__slots__ = (
		'category',
		'products',
		'categories',
		'page_info'
	)

	@staticmethod
	@param_required(['webapp_owner', 'category_id', "cur_page"])
	def get(args):
		"""
		工厂方法，获得与category_id对应的SimpleProducts业务对象

		@param[in] webapp_owner
		@param[in] category_id: 商品分类的id
		@param[in] cur_page: 第几页码数据

		@return SimpleProducts业务对象
		"""
		webapp_owner = args['webapp_owner']
		category_id = int(args['category_id'])
		cur_page = int(args['cur_page'])
		
		products = NewSimpleProducts(webapp_owner, category_id, cur_page)
		return products

	def __init__(self, webapp_owner, category_id, cur_page):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		# jz 2015-11-26
		# self.context['webapp_user'] = webapp_user

		self.category, self.products, self.categories, self.page_info = self.__get_from_cache(category_id, cur_page)

	def __get_from_cache(self, category_id, cur_page):
		"""
		从缓存中获取数据
		"""
		webapp_owner = self.context['webapp_owner']
		
		page_info, products = self.__get_products_by_category(category_id, webapp_owner.id, cur_page)
		categories = self.__get_categories(corp_id=webapp_owner.id)
		if category_id == 0:
			category = mall_models.ProductCategory()
			category.name = u'全部'
			category.id = 0
		else:
			# TODO 发消息方式
			category = mall_models.ProductCategory.select().dj_where(id=category_id).first()
			if not category:
				category = mall_models.ProductCategory()
				category.name = u'已删除分类'
				category.is_deleted = True
				category.id = category_id

		return category, products, categories, page_info

	def __get_products_by_category(self, category_id, corp_id, cur_page):
		"""
		
		根据商品分类获取商品简单信息
		"""
		key = '{wo:%s}_{co:%s}_pids' % (corp_id, category_id)
		cache_no_data = False
		if not cache_util.exists_key(key):
			cache_no_data = True
			# 发送消息让manager_cache缓存分组数据
			topic_name = settings.TOPIC_NAME
			msg_name = 'refresh_category_product'
			data = {
				"corp_id": corp_id,
				"category_id": category_id
			}
			msgutil.send_message(topic_name, msg_name, data)
		
		# if not cache_util.exists_key('all_simple_effective_products'):
		#
		# 	# TODO发送消息让manager_cache缓存所有简单商品数据
		# 	topic_name = settings.TOPIC_NAME
		# 	msg_name = 'refresh_all_simple_products'
		#
		# 	msgutil.send_message(topic_name, msg_name, {})
		# 	cache_no_data = True
				
		product_ids = list(redis_util.lrange(key, 0, -1))
		if product_ids and product_ids[0] == 'NONE':
			# 说明分组无商品
			page_info, page_product_ids = paginator.paginate([], cur_page, 6)
			
			return page_info, []
		# 获取分页信息
		page_info, page_product_ids = paginator.paginate(product_ids, cur_page, 6)
		# 有缓存缓存但是缓存里没有数据
		if not page_product_ids and not cache_no_data:
			return page_info, []
		if cache_no_data:
			# 缓存key都不在,
			return page_info, None
		keys = [':1:apiproduct_simple_detail_{pid:%s}' % product_id for product_id in page_product_ids]
		
		redis_products = redis_util.mget(keys)
		# 缓存没有此商品详情的key,故需mall_cache_manager缓存数据
		no_redis_product_ids = [page_product_ids[index] for index, r in enumerate(redis_products) if r is None]
		if no_redis_product_ids:
			cache_no_data = True
			# 发送消息让manager_cache缓存分组数据
			topic_name = settings.TOPIC_NAME
			msg_name = 'refresh_product_detail'
			data = {
				"corp_id": corp_id,
				"product_ids": no_redis_product_ids
			}
			msgutil.send_message(topic_name, msg_name, data)
		if cache_no_data:
			# products is Nond 的时候要显示缓存无数据所以这里是返回None
			page_info, page_product_ids = paginator.paginate([], cur_page, 6)
			return page_info, None
		products = [pickle.loads(product) for product in redis_products]
		result = sorted(products, key=lambda k: page_product_ids.index(str(k.get('id'))))
		# 判断社群平台是否是"固定底价+溢价"类型平台
		for product in result:
			temp_key = "customized_price_{wo:%s}_{pid:%s}" % (corp_id, product.get('id'))
			customized_price = cache_util.get_cache(temp_key)
			if cache_util.get_cache(temp_key):
				product['display_price'] = customized_price
		return page_info, result

	def __get_categories(self, corp_id):
		key = 'categories_%s' % corp_id
		categories = redis_util.hgetall(key)
		return [dict(id=k,
					 name=v) for k, v in categories.items()]
	