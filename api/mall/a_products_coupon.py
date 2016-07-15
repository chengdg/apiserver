# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
#import resource
from business.mall.simple_products import SimpleProducts
from business.mall.coupon.coupon_rule import CouponRule
class AProducts(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'products_coupon'

	@param_required(['coupon_rule_id'])
	def get(args):
		"""
		获取多商品券下的商品

		@param coupon_rule_id CouponRuleID
		@return {
			'categories': simple_products.categories,
			'products': simple_products.products,
			'category': category_dict}
		"""
		webapp_owner = args['webapp_owner']
		cur_page = args['cur_page']
		count_per_page = args['count_per_page']

		coupon_rule_id = int(args['coupon_rule_id'])
		coupon_rule = CouponRule.from_id({
			'id': coupon_rule_id
			})
		product_ids = map(lambda x: int(x), coupon_rule.limit_product_id.split(',')) #多商品券下的商品id

		page_info,products_data, category, categories,  = SimpleProducts.get_for_coupon({
			"webapp_owner": webapp_owner,
			'product_ids': product_ids,
			'cur_page': cur_page,
			'count_per_page': count_per_page
		})


		# simple_products = SimpleProducts.get({
		# 	"webapp_owner": webapp_owner,
		# 	"category_id": category_id,
		# })
		# products = [product for product in simple_products.products if product['id'] in product_ids]
		# category_dict = category.to_dict('is_deleted')
		return {
			'coupon_rule_name': coupon_rule.name,
			'products': products_data,
			'page_info':page_info.to_dict(),
			# 'category': category_dict,
			# 'categories': categories,

		}
