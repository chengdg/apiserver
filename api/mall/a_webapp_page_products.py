# -*- coding: utf-8 -*-

import json

from eaglet.core import api_resource
from eaglet.decorator import param_required
from eaglet.core import paginator
#import resource
from business.mall.product_search import ProductSearch
from business.mall.simple_products import SimpleProducts
from business.mall.webapp_page_products import WebAppPageProducts
from business.mall.new_product_search import NewProductSearch


class AWebAppPageProducts(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'webapp_page_products'

	def get(args):
		"""
	
		"""
		product_ids = args.get('product_ids', '[]')
		count_per_page = args.get('count_per_page', -1)
		category_id = args.get('category_id', 0)
		product_ids = json.loads(product_ids)
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		instance = WebAppPageProducts(webapp_owner, webapp_user)
		products = []
		if product_ids:
			products = instance.get_by_product_ids(product_ids=product_ids)
			
			return products
		print products
		if count_per_page > 0:
			products = instance.get_by_category(category_id=category_id, count_per_page=count_per_page)
		# 'id': db_product.id,
		# 'name': db_product.name,
		# 'is_deleted': product.is_deleted,
		# 'thumbnails_url': product.thumbnails_url,
		# # 商品的规格已经处理过改价
		# 'display_price': product.price_info['display_price']
		return {
			'products': products,
		}
