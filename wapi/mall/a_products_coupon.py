# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
#import resource
from business.mall.simple_products import SimpleProducts
from business.mall.coupon.coupon_rule import CouponRule
class AProducts(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'products_coupon'

	@param_required(['category_id', 'coupon_rule_id'])
	def get(args):
		"""
		获取多商品券下的商品

		@param coupon_rule_id CouponRuleID
		@return {
			'categories': simple_products.categories,
			'products': simple_products.products,
			'category': category_dict}
		"""
		category_id = args['category_id']
		webapp_owner = args['webapp_owner']
		coupon_rule_id = int(args['coupon_rule_id'])
		coupon_rule = CouponRule.from_id({
			'id': coupon_rule_id
			})
		product_ids = map(lambda x: int(x), coupon_rule.limit_product_id.split(',')) #多商品券下的商品id
		simple_products = SimpleProducts.get({
			"webapp_owner": webapp_owner,
			"category_id": category_id,
		})
		products = [product for product in simple_products.products if product['id'] in product_ids]
		category_dict = simple_products.category.to_dict('is_deleted')
		return {
			'categories': simple_products.categories,
			'products': products,
			'category': category_dict
		}
