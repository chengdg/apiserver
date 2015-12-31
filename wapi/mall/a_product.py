# -*- coding: utf-8 -*-
import json

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from utils import dateutil as utils_dateutil
#import resource
from business.mall.product import Product
from business.mall.review.product_reviews import ProductReviews


class AProduct(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'product'


	@param_required(['product_id'])
	def get(args):
		"""
		获取商品详情

		@param id 商品ID

		@note 从Weapp中迁移过来
		@see  mall_api.get_product_detail(webapp_owner_id, product_id, webapp_user, member_grade_id)
		"""

		"""
		显示“商品详情”页面

		"""
		product_id = args['product_id']
		webapp_owner = args['webapp_owner']

		product = Product.from_id({
			'webapp_owner': webapp_owner,
			# 'member': member,
			'product_id': args['product_id']
		})
		if product.is_deleted:
			return {'is_deleted': True}
		else:
			product.apply_discount(args['webapp_user'])

			product_reviews = ProductReviews.get_from_product_id({
				'webapp_owner': webapp_owner,
				'product_id': product_id,
			})
			if product_reviews:
				reviews = product_reviews.products
			else:
				reviews = []

			result = product.to_dict(extras=['hint'])

			result['webapp_owner_integral_setting'] = {
				'integarl_per_yuan': webapp_owner.integral_strategy_settings.integral_each_yuan
			}
			result['product_reviews'] = reviews

		return result
