# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
#import resource
from business.mall.product_search import ProductSearch
from business.mall.simple_products import SimpleProducts

class AProducts(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'products'

	@param_required(['category_id'])
	def get(args):
		"""
		获取商品详情

		@param category_id 商品分类ID
		@return {
			'categories': simple_products.categories,
			'products': simple_products.products,
			'category': category_dict}
		"""
		category_id = args['category_id']
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']

		product_name = args.get('product_name', None)
		product_ids = args.get('product_ids', None)

		simple_products = SimpleProducts.get({
			"webapp_owner": webapp_owner,
			"category_id": category_id,
		})

		products = simple_products.products

		if product_name:
			# 商品搜索
			searcher = ProductSearch.get({
				"webapp_owner": webapp_owner,
				"webapp_user": webapp_user
			})
			products = searcher.filter_products({'products': products, 'product_name': product_name})

		if product_ids:
			product_ids = map(lambda x: int(x), product_ids.split(','))
			products = filter(lambda x: x['id'] in product_ids, products)

		category_dict = simple_products.category.to_dict('is_deleted')
		return {
			'categories': simple_products.categories,
			'products': products,
			'category': category_dict,
			'mall_config': webapp_owner.mall_config,

		}
