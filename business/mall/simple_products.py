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
# from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util

from business.mall.product_search import ProductSearch
from db.mall import models as mall_models
from eaglet.core import watchdog
from business import model as business_model
import settings
from business.mall.product import Product
from eaglet.core import  query_paginator


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
	@param_required(['webapp_owner', 'product_ids', 'cur_page', 'count_per_page'])
	def get_for_coupon(args):
		cur_page = int(args['cur_page'])
		count_per_page = int(args['count_per_page'])
		webapp_owner_id = args['webapp_owner'].id
		product_ids = args['product_ids']
		product_models = mall_models.Product.select().dj_where(
			owner=webapp_owner_id,
			shelve_type=mall_models.PRODUCT_SHELVE_TYPE_ON,
			is_deleted=False,
			id__in=product_ids
		)
		page_info, product_models = query_paginator.paginate(product_models, cur_page, count_per_page)

		product_data = SimpleProducts.__get_product_data(
			{'product_models': product_models, 'webapp_owner': args['webapp_owner']})

		return page_info, product_data

	@staticmethod
	@param_required(['webapp_owner', 'category_id', 'cur_page', 'count_per_page'])
	def get_for_list(args):

		webapp_owner = args['webapp_owner']
		category_id = int(args['category_id'])
		cur_page = int(args['cur_page'])
		count_per_page = int(args['count_per_page'])

		if category_id == 0:
			product_models = mall_models.Product.select().dj_where(
				owner=webapp_owner.id,
				shelve_type=mall_models.PRODUCT_SHELVE_TYPE_ON,
				is_deleted=False,
			).order_by(mall_models.Product.display_index,
			           -mall_models.Product.id)

			page_info, product_models = query_paginator.paginate(product_models, cur_page, count_per_page)

		else:
			category_has_products = mall_models.CategoryHasProduct.select().join(mall_models.Product).where(
				mall_models.CategoryHasProduct.category == category_id,
				mall_models.CategoryHasProduct.display_index > 0,
				mall_models.Product.shelve_type == mall_models.PRODUCT_SHELVE_TYPE_ON,
				mall_models.Product.is_deleted == False
			).order_by('display_index', 'created_at')

			page_info, category_has_products = query_paginator.paginate(category_has_products, cur_page, count_per_page)

			product_ids = [p.product_id for p in category_has_products]

			product_models = mall_models.Product.select().dj_where(id__in=product_ids)

		products_data = SimpleProducts.__get_product_data({
			'product_models': product_models,
			'webapp_owner': args['webapp_owner']
		})

		return page_info, products_data


	@staticmethod
	@param_required(['webapp_owner', 'category_id', 'cur_page', 'count_per_page','product_name'])
	def get_for_search(args):

		webapp_owner = args['webapp_owner']
		cur_page = int(args['cur_page'])
		count_per_page = int(args['count_per_page'])
		product_name = args['product_name']

		product_models = mall_models.Product.select().where(
			mall_models.Product.owner==webapp_owner.id,
			mall_models.Product.shelve_type==mall_models.PRODUCT_SHELVE_TYPE_ON,
			mall_models.Product.is_deleted==False,
			mall_models.Product.name.contains(product_name)
		)

		page_info, product_models = query_paginate(product_models, cur_page, count_per_page)

		products_data = SimpleProducts.__get_product_data({
			'product_models': product_models,
			'webapp_owner': args['webapp_owner']
		})

		ProductSearch.log_record({
			'webapp_user_id':args['webapp_user'].id,
			'webapp_owner_id':webapp_owner.id,
			'product_name':product_name

		})

		return page_info, products_data


	@staticmethod
	@param_required(['webapp_owner', 'category_id'])
	def get_categories(args):
		webapp_owner_id = args['webapp_owner'].id
		category_id = args['category_id']
		categories = mall_models.ProductCategory.select().dj_where(owner=webapp_owner_id)

		categories = [{"id": category.id, "name": category.name} for category in categories]
		# 获得当前分类信息
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

		category = category.to_dict('is_deleted')

		return categories, category

	@staticmethod
	@param_required(['webapp_owner', 'product_models'])
	def __get_product_data(args):
		webapp_owner = args['webapp_owner']
		# 根据后台设置是否填充销量
		show_product_sales = webapp_owner.mall_config['show_product_sales']

		products = Product.from_models({
			'webapp_owner': webapp_owner,
			'models': args['product_models'],
			'fill_options': {
				"with_price": True,
				"with_product_promotion": True,
				"with_selected_category": True,
				"with_sales": show_product_sales
			}
		})

		products_data = []

		for product in products:
			products_data.append({
				"id": product.id,
				"name": product.name,
				"is_member_product": product.is_member_product,
				"display_price": product.price_info['display_price'],
				"promotion_js": json.dumps(product.promotion.to_dict()) if product.promotion else json.dumps(None),
				"thumbnails_url": product.thumbnails_url,
				"sales": product.sales
			})

		return products_data
