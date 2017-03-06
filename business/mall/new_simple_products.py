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
		# jz 2015-11-26
		# webapp_user = self.context['webapp_user']
		key = 'webapp_products_categories_{wo:%s}' % webapp_owner.id
		# data = cache_util.get_from_cache(key, self.__get_from_db(webapp_owner))
		page_info, products = self.__get_products_by_category(category_id, webapp_owner.id, cur_page)
		# print '===========>', products
		categories = self.__get_categories(corp_id=webapp_owner.id)
		if category_id == 0:
			category = mall_models.ProductCategory()
			category.name = u'全部'
			category.id = 0
		else:
			id2category = dict([(c["id"], c) for c in categories])
			if category_id in id2category:
				category_dict = id2category[category_id]
				category = mall_models.ProductCategory()
				category.id = category_dict['id']
				category.name = category_dict['name']
				category.is_deleted = False
			else:
				category = mall_models.ProductCategory()
				category.is_deleted = True
				category.name = u'已删除分类'

		return category, products, categories, page_info

	def __get_from_db(self, webapp_owner):
		"""
		从数据库中获取需要存储到缓存中的数据
		@warning 如修改此处,务必同步修改weapp中的cache/webapp_cache.py update_product_list_cache()
		"""
		def inner_func():
			webapp_owner_id = webapp_owner.id
			watchdog.warning({
				'uuid': 'product_list_cahce',
				'hint': '商品列表页未命中缓存',
				'woid': webapp_owner_id
			})

			product_models = self.__get_products(webapp_owner_id, 0)

			categories = mall_models.ProductCategory.select().dj_where(owner=webapp_owner_id)

			product_ids = [product_model.id for product_model in product_models]
			category_has_products = mall_models.CategoryHasProduct.select().dj_where(product__in=product_ids)
			product2categories = dict()
			for relation in category_has_products:
				product2categories.setdefault(relation.product_id, set()).add(relation.category_id)

			try:
				categories = [{"id": category.id, "name": category.name} for category in categories]

				# Fill detail
				product_datas = []
				# jz 2015-11-26
				# member = webapp_user.member

				products = Product.from_models({
					'webapp_owner': webapp_owner,
					'models': product_models,
					'fill_options': {
						"with_price": True,
						"with_product_promotion": True,
						"with_selected_category": True
					}
				})
				# for product_model in product_models:
				# 	product = Product.from_model({
				# 		'webapp_owner': webapp_owner,
				# 		'model': product_model,
				# 		'fill_options': {
				# 			"with_price": True,
				# 			"with_product_promotion": True,
				# 			"with_selected_category": True
				# 		}
				# 	})
				#
				for product in products:
					product_datas.append({
						"id": product.id,
						"name": product.name,
						"is_member_product": product.is_member_product,
						"display_price": product.price_info['display_price'],
						"promotion_js": json.dumps(product.promotion.to_dict()) if product.promotion else json.dumps(None),
						"thumbnails_url": product.thumbnails_url,
						"supplier": product.supplier,
						"categories": list(product2categories.get(product.id, []))
					})

				# delete by bert at 2016715
				# for product_data in product_datas:
				# 	product_data['categories'] = list(product2categories.get(product_data['id'], []))

				return {
					'value': {
						"products": product_datas,
						"categories": categories
					}
				}
			except:
				from eaglet.core.exceptionutil import unicode_full_stack
				msg = {
					'traceback': unicode_full_stack(),
					'hint': u'获取商品列表mysql数据失败',
					'msg_id': 'spdb123',
					'woid': webapp_owner_id
				}
				watchdog.alert(msg)
				if settings.DEBUG:
					raise
				else:
					return None
		return inner_func

	def __get_products(self, webapp_owner_id, category_id):
		"""
		get_products: 获得product集合
		@warning 如修改此处,务必同步修改weapp中的cache/webapp_cache.py update_product_list_cache()
		最后修改：闫钊
		"""
		#获得category和product集合
		category = None
		products = None

		mall_type = self.context['webapp_owner'].mall_type
		if category_id == 0:
			if mall_type:
				pool_products = mall_models.ProductPool.select().dj_where(woid=webapp_owner_id, status=mall_models.PP_STATUS_ON)
				pool_product2display_index = dict([(p.product_id, p.display_index) for p in pool_products])
				if pool_product2display_index:
					products = mall_models.Product.select().where((mall_models.Product.id << pool_product2display_index.keys())|
						( (mall_models.Product.owner == webapp_owner_id) & (mall_models.Product.shelve_type == mall_models.PRODUCT_SHELVE_TYPE_ON) & (mall_models.Product.is_deleted == False) & (mall_models.Product.type.not_in([mall_models.PRODUCT_DELIVERY_PLAN_TYPE])))).order_by(mall_models.Product.display_index, -mall_models.Product.id)
					#处理排序 TODO bert 优化
					product_list = []
					for product in products:
						if product.id in pool_product2display_index.keys():
							product.display_index = pool_product2display_index[product.id]
						if product.display_index == 0:
							product.display_index = 99999999
						product_list.append(product)
					product_list.sort(lambda x,y: cmp(x.display_index, y.display_index))

					products = product_list

			if products is None:
				products = mall_models.Product.select().dj_where(
					owner = webapp_owner_id, 
					shelve_type = mall_models.PRODUCT_SHELVE_TYPE_ON, 
					is_deleted = False,
					type__not = mall_models.PRODUCT_DELIVERY_PLAN_TYPE).order_by(mall_models.Product.display_index, -mall_models.Product.id)
				# jz 2015-11-26
				# if not is_access_weizoom_mall:
				# 	# 非微众商城
				# 	product_ids_in_weizoom_mall = self.__get_product_ids_in_weizoom_mall(webapp_id)
				# 	products.dj_where(id__notin = product_ids_in_weizoom_mall)

				products_0 = products.dj_where(display_index=0)

				products_not_0 = products.dj_where(display_index__not=0)
				# TODO: need to be optimized
				products = list(itertools.chain(products_not_0, products_0))

			category = mall_models.ProductCategory()
			category.name = u'全部'
		else:
			watchdog.alert('过期的方法分支module_api.get_products_in_webapp else', type='mall')
			# jz 2015-11-26
			# try:
			# if not is_access_weizoom_mall:
			# 	# 非微众商城
			# 	product_ids_in_weizoom_mall = self.__get_product_ids_in_weizoom_mall(webapp_id)
			# 	other_mall_product_ids_not_checked = []
			# else:
			# 	product_ids_in_weizoom_mall = []
			# 	_, other_mall_product_ids_not_checked = self.__get_not_verified_weizoom_mall_partner_products_and_ids(webapp_id)

			category = mall_models.ProductCategory.get(mall_models.ProductCategory.id==category_id)
			category_has_products = mall_models.CategoryHasProduct.select().dj_where(category=category)
			products_0 = []  # 商品排序， 过滤0
			products_not_0 = []  # 商品排序， 过滤!0
			for category_has_product in category_has_products:
				if category_has_product.product.shelve_type == mall_models.PRODUCT_SHELVE_TYPE_ON:
					#TODO2: for循环中的外键数据库查询，需要优化
					product = category_has_product.product
					#过滤已删除商品和套餐商品
					if(product.is_deleted or product.type == mall_models.PRODUCT_DELIVERY_PLAN_TYPE or
								product.id in product_ids_in_weizoom_mall or
								product.id in other_mall_product_ids_not_checked or
								product.shelve_type != mall_models.PRODUCT_SHELVE_TYPE_ON):
						continue
					# # 商品排序， 过滤
					if product.display_index == 0:
						products_0.append(product)
					else:
						products_not_0.append(product)
			# 处理商品排序
			products_0 = sorted(products_0, key=operator.attrgetter('id'), reverse=True)
			products_not_0 = sorted(products_not_0, key=operator.attrgetter('display_index'))
			products = products_not_0 + products_0
			# except :
			# 	products = []
			# 	category = ProductCategory()
			# 	category.is_deleted = True
			# 	category.name = u'全部'
		# jz 2015-11-26
		#处理search信息
		# if 'search_info' in options:
		# 	query = options['search_info']['query']
		# 	if query:
		# 		conditions = {}
		# 		conditions['name__contains'] = query
		# 		products = products.filter(**conditions)
		return products
	# jz 2015-11-26
	# def __get_product_ids_in_weizoom_mall(self, webapp_id):
	# 	return [weizoom_mall_other_mall_product.product_id for weizoom_mall_other_mall_product in mall_models.WeizoomMallHasOtherMallProduct.select().dj_where(webapp_id=webapp_id)]
	# def __get_weizoom_mall_partner_products_and_ids(self, webapp_id):
	# 	"""
	# 	获取该微众商城下的合作商家加入到微众商城的商品
	# 	"""
	# 	return self.__get_weizoom_mall_partner_products_and_ids_by(webapp_id)
	# def __get_verified_weizoom_mall_partner_products_and_ids(self, webapp_id):
	# 	return self.__get_weizoom_mall_partner_products_and_ids_by(webapp_id, True)
	# def __get_not_verified_weizoom_mall_partner_products_and_ids(self, webapp_id):
	# 	return self.__get_weizoom_mall_partner_products_and_ids_by(webapp_id, False)
	# def __get_weizoom_mall_partner_products_and_ids_by(self, webapp_id, is_checked=None):
	# 	if mall_models.WeizoomMall.select().dj_where(webapp_id=webapp_id).count() > 0:
	# 		weizoom_mall = mall_models.WeizoomMall.select().dj_where(webapp_id=webapp_id)[0]
	# 		product_ids = []
	# 		product_check_dict = dict()
	# 		other_mall_products = mall_models.WeizoomMallHasOtherMallProduct.select().dj_where(weizoom_mall=weizoom_mall)
	# 		if is_checked != None:
	# 			 other_mall_products.dj_where(is_checked=is_checked)
	# 		for other_mall_product in other_mall_products:
	# 			product_check_dict[other_mall_product.product_id] = other_mall_product.is_checked
	# 			product_ids.append(other_mall_product.product_id)
	# 		products = mall_models.Product.select().dj_where(id__in=product_ids, shelve_type=mall_models.PRODUCT_SHELVE_TYPE_ON, is_deleted=False)
	# 		for product in products:
	# 			product.is_checked = product_check_dict[product.id]
	# 		return products, product_ids
	# 	else:
	# 		return None, None

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
		
		return page_info, result

	def __get_categories(self, corp_id):
		key = 'categories_%s' % corp_id
		categories = redis_util.hgetall(key)
		return [dict(id=k,
					 name=v) for k, v in categories.items()]
	