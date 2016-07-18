# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
# import resource
from business.mall.product_search import ProductSearch
from business.mall.simple_products import SimpleProducts
from business.mall.coupon.coupon_rule import CouponRule


class AProducts(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'products'

	# @param_required(['category_id'])
	# def get(args):
	# 	"""
	# 	获取商品详情
	#
	# 	@param category_id 商品分类ID
	# 	@return {
	# 		'categories': simple_products.categories,
	# 		'products': simple_products.products,
	# 		'category': category_dict}
	# 	"""
	# 	category_id = args['category_id']
	# 	webapp_owner = args['webapp_owner']
	# 	webapp_user = args['webapp_user']
	#
	# 	product_name = args.get('product_name', None)
	#
	# 	simple_products = SimpleProducts.get({
	# 		"webapp_owner": webapp_owner,
	# 		"category_id": category_id,
	# 	})
	#
	# 	products = simple_products.products
	#
	# 	if product_name:
	# 		# 商品搜索
	# 		searcher = ProductSearch.get({
	# 			"webapp_owner": webapp_owner,
	# 			"webapp_user": webapp_user
	# 		})
	# 		products = searcher.filter_products({'products': products, 'product_name': product_name})
	#
	# 	category_dict = simple_products.category.to_dict('is_deleted')
	# 	return {
	# 		'categories': simple_products.categories,
	# 		'products': products,
	# 		'category': category_dict,
	# 		'mall_config': webapp_owner.mall_config,
	#
	# 	}

	@param_required(['count_per_page', 'cur_page'])
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
		cur_page = args['cur_page']
		count_per_page = args['count_per_page']
		product_name = args.get('product_name', None)
		coupon_rule_id = args.get('coupon_rule_id', None)

		if product_name:
			page_info, products = SimpleProducts.get_for_search({
				"webapp_owner": webapp_owner,
				'webapp_user_id': webapp_user.id,
				'product_name': product_name,
				'cur_page': cur_page,
				'count_per_page': count_per_page
			})
		elif coupon_rule_id:
			coupon_rule = CouponRule.from_id({
				'id': int(coupon_rule_id)
			})
			product_ids = map(lambda x: int(x), coupon_rule.limit_product_id.split(','))  # 多商品券下的商品id

			page_info, products = SimpleProducts.get_for_coupon({
				"webapp_owner": webapp_owner,
				'product_ids': product_ids,
				'cur_page': cur_page,
				'count_per_page': count_per_page
			})
		else:
			page_info, products = SimpleProducts.get_for_list({
				"webapp_owner": webapp_owner,
				"category_id": int(category_id),
				'cur_page': cur_page,
				'count_per_page': count_per_page
			})

		# products = simple_products.products

		# if product_name:
		# 	# 商品搜索
		# 	searcher = ProductSearch.get({
		# 		"webapp_owner": webapp_owner,
		# 		"webapp_user": webapp_user
		# 	})
		# 	products = searcher.filter_products({'products': products, 'product_name': product_name})
		categories, category = SimpleProducts.get_categories({'webapp_owner': webapp_owner,'category_id':category_id})

		return {
			'categories': categories,
			'products': products,
			'category': category,
			'mall_config': webapp_owner.mall_config,
			'page_info': page_info.to_dict()

		}
