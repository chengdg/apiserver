#coding: utf8
"""@package wapi.mall.a_product_review
商品评论暴露的API

"""

#import copy
#from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
#from db.mall import models as mall_models
#from db.mall import promotion_models
#from utils import dateutil as utils_dateutil
#import resource
#from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
#from core.cache import utils as cache_utils
#from business.mall.order_factory import OrderFactory
#from business.mall.purchase_info import PurchaseInfo
#from business.mall.pay_interface import PayInterface
from business.mall.order_review import OrderReview
from business.mall.product_review import ProductReview
import logging
#from core.watchdog.utils import watchdog_info

class AProductReviews(api_resource.ApiResource):
	"""
	获取商品的评论列表
	"""
	app = 'mall'
	resource = 'product_reviews'

	@staticmethod
	def to_dict(product_review):
		"""
		将ProductReview转成dict
		"""
		# TODO: 实现to_dict()
		#return product_review.to_dict()
		return {
			"status": product_review.status,
			"order_review_id": product_review.order_review_id,
			"product_id": product_review.product_id,
			"order_id": product_review.product_id,
			"created_at": product_review.created_at,
			"product_score": product_review.product_score,
			"review_detail": product_review.review_detail,
			"order_has_product_id": product_review.order_has_product_id,
			"member_id": product_review.member_id,
			"id": product_review.id,
			"top_name": product_review.top_name
        	}

	@param_required(['woid', 'product_id'])
	def get(args):
		"""
		获取审核通过的product review

		@note 在原Webapp中，review是包括product detail(商品详情)的`product`中。见`request_util.py:get_product()`。获得`product`需要woid, product_id, member_grade_id, wuid四项参数。实际通过`mall/module_api.py:get_product_detail()`获得product detail。而`get_product_detail()`调用`get_webapp_product_detail()`组装product detail。
		在`get_product_detail_for_cache()`找到`product_review`
		"""
		webapp_owner = args['webapp_owner']
		product_id = args['product_id']
		limit = args.get('limit', 2)
		
		product_reviews = ProductReview.get_latest_product_reviews({
				'webapp_owner': webapp_owner,
				'product_id': product_id,
				'limit': limit,
			})
		#product_reviews = ProductReview.from_id({
		#	'webapp_owner': webapp_owner,
		#	'product_id': product_id
		#	})
		data = [AProductReviews.to_dict(product_review) for product_review in product_reviews]
		return {
			'reviews': data
		}
