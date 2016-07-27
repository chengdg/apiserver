# -*- coding: utf-8 -*-
"""@package business.mall.simple_products
携带基础商品信息的商品集合，用于商品列表页面的展示
"""

import json
from bs4 import BeautifulSoup
import math
import itertools
from operator import attrgetter

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from eaglet.core import watchdog
from business import model as business_model 
import settings
from business.mall.product import Product


class SimpleProducts(business_model.Model):
	"""
	携带基础商品信息的商品集合
	"""
	__slots__ = (
		'category',
		'products',
		'categories'
	)

	@staticmethod
	@param_required(['webapp_owner', 'category_id'])
	def get(args):
		"""
		工厂方法，获得与category_id对应的SimpleProducts业务对象

		@param[in] webapp_owner
		@param[in] category_id: 商品分类的id

		@return SimpleProducts业务对象
		"""
		webapp_owner = args['webapp_owner']
		category_id = int(args['category_id'])
		
		products = SimpleProducts(webapp_owner, category_id)
		return products

	def __init__(self, webapp_owner, category_id):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		# jz 2015-11-26
		# self.context['webapp_user'] = webapp_user

		self.category, self.products, self.categories = self.__get_from_cache(category_id)

	def __get_from_cache(self, category_id):
		"""
		从缓存中获取数据
		"""
		webapp_owner = self.context['webapp_owner']
		# jz 2015-11-26
		# webapp_user = self.context['webapp_user']
		key = 'webapp_products_categories_{wo:%s}' % webapp_owner.id
		data = cache_util.get_from_cache(key, self.__get_from_db(webapp_owner))
		products = data['products']

		if category_id == 0:
			category = mall_models.ProductCategory()
			category.name = u'全部'
			category.id = 0
		else:
			id2category = dict([(c["id"], c) for c in data['categories']])
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
		# jz 2015-11-26
		#products = mall_models.Product.from_list(data['products'])
		# if category_id != 0:
			products = [product for product in products if category_id in product['categories']]

			# 分组商品排序
			products_id = map(lambda p: p['id'], products)
			chp_list = mall_models.CategoryHasProduct.select().dj_where(category_id=category_id, product__in=products_id)
			product_id2chp = dict(map(lambda chp: (chp.product_id, chp), chp_list))
			for product in products:
				product['display_index'] = product_id2chp[product['id']].display_index
				product['join_category_time'] = product_id2chp[product['id']].created_at

			# 1.shelve_type, 2.display_index, 3.id
			products_is_0 = filter(lambda p: p['display_index'] == 0, products)
			products_not_0 = filter(lambda p: p['display_index'] != 0, products)
			products_is_0 = sorted(products_is_0, key=lambda x: x['join_category_time'], reverse=True)
			products_not_0 = sorted(products_not_0, key=lambda x: x['display_index'])

			products = products_not_0 + products_is_0

		product_sales = mall_models.ProductSales.select().dj_where(product__in=[p['id'] for p in products])
		product_id2sales = {t.product_id: t.sales for t in product_sales}

		for p in products:
			p['sales'] = product_id2sales.get(p['id'], 0)   # warning,没产生销量的商品没有创建ProductSales记录

		return category, products, data['categories']


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
				if settings.DEBUG:
					raise
				else:
					return None
		return inner_func

	def __get_products(self, webapp_owner_id, category_id):
		"""
		get_products: 获得product集合

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

