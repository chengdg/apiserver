#coding: utf8
"""@package apimall.a_product_review
商品评论暴露的API

"""

from eaglet.core import api_resource
from eaglet.decorator import param_required
from business.mall.review.product_reviews import ProductReviews
import logging

class AProductReviews(api_resource.ApiResource):
	"""
	获取商品的评论列表(废弃，代码迁移到营销工具中了)
	"""
	app = 'mall'
	resource = 'product_reviews'


	@param_required(['product_id'])
	def get(args):
		"""
		获取审核通过的product review
		@param product_id
		@return {'reviews': }
		@note 在原Webapp中，review是包括product detail(商品详情)的`product`中。见`request_util.py:get_product()`。获得`product`需要woid, product_id, member_grade_id, wuid四项参数。实际通过`mall/module_api.py:get_product_detail()`获得product detail。而`get_product_detail()`调用`get_webapp_product_detail()`组装product detail。
		在`get_product_detail_for_cache()`找到`product_review`
		"""
		webapp_owner = args['webapp_owner']
		product_id = args['product_id']
		limit = args.get('limit', 2)
		
		product_reviews = ProductReviews.get_from_product_id({
				'webapp_owner': webapp_owner,
				'product_id': product_id,
			})
		
		products = product_reviews.products
		# if limit and products:
		# 	products = products[:2]

		return {
			'reviews': products
		}
