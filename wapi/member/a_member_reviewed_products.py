#coding: utf8
"""@package wapi.mall.a_member_reviewed_products.AMemberReviewedProducts
商品评论暴露的API

"""

#import copy
#from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from business.mall.order_review import OrderReview
from business.mall.review.reviewed_products import ReviewedProducts
import logging
#from core.watchdog.utils import watchdog_info

class AMemberReviewedProducts(api_resource.ApiResource):
	"""
	获取商品的评论列表
	"""
	app = 'member'
	resource = 'reviewed_products'

	@param_required(['webapp_owner', 'webapp_user'])
	def get(args):
		"""
		得到商品评价列表

		@note 在原Webapp中，get_product_review_list()
		"""


		reviewed_products = ReviewedProducts.get_for_webapp_user({
			'webapp_owner': args['webapp_owner'],
			'webapp_user': args['webapp_user']
			})

		return {
			'reviewed_products': reviewed_products.products
		}
