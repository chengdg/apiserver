# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
#import resource
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

		simple_products = SimpleProducts.get({
			"webapp_owner": webapp_owner,
			"category_id": category_id,
		})

		category_dict = simple_products.category.to_dict('is_deleted')
		return {
			'categories': simple_products.categories,
			'products': simple_products.products,
			'category': category_dict,
			'mall_config': webapp_owner.mall_config,
		}
