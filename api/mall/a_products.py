# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
#import resource
from business.mall.product_search import ProductSearch
from business.mall.simple_products import SimpleProducts
from business.mall.new_simple_products import NewSimpleProducts
from business.mall.new_product_search import NewProductSearch

class AProducts(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'products'

	@param_required(['category_id'])
	def get(args):
		"""
		获取商品列表

		@param category_id 商品分类ID
		@return {
			'categories': simple_products.categories,
			'products': simple_products.products,
			'category': category_dict}
		"""
		category_id = args['category_id']
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		cur_page = args.get('cur_page', 1)
		count_per_page = args.get('count_per_page', 6)
		webapp_type = webapp_owner.user_profile.webapp_type
		product_name = args.get('product_name', None)
		if webapp_type == 1:
			# 自营平台
			simple_products = NewSimpleProducts.get({
				"webapp_owner": webapp_owner,
				"category_id": category_id,
				"cur_page": cur_page
			})
	
			products = simple_products.products
			if products is None or simple_products.page_info is None:
				return {
					'categories': simple_products.categories,
					'products': products,
					'category': category_dict,
					'mall_config': webapp_owner.mall_config,
					"no_cache": True
				}
			if product_name:
				# 商品搜索
				searcher = NewProductSearch.get({
					"webapp_owner": webapp_owner,
					"webapp_user": webapp_user,
					"cur_page": cur_page
				})
				products = searcher.search_products(category_id, cur_page, product_name)
	
			category_dict = simple_products.category.to_dict('is_deleted')
			return {
				'categories': simple_products.categories,
				'products': products,
				'category': category_dict,
				'mall_config': webapp_owner.mall_config,
				"no_cache": False
			}
		else:
			simple_products = SimpleProducts.get({
				"webapp_owner": webapp_owner,
				"category_id": category_id,
			})
			
			products = simple_products.products
			if products is None or simple_products.page_info is None:
				return {
					'categories': simple_products.categories,
					'products': products,
					'category': category_dict,
					'mall_config': webapp_owner.mall_config,
				}
			if product_name:
				# 商品搜索
				searcher = ProductSearch.get({
					"webapp_owner": webapp_owner,
					"webapp_user": webapp_user
				})
				products = searcher.filter_products({'products': products, 'product_name': product_name})
			
			category_dict = simple_products.category.to_dict('is_deleted')
			return {
				'categories': simple_products.categories,
				'products': products,
				'category': category_dict,
				'mall_config': webapp_owner.mall_config,
				
			}

