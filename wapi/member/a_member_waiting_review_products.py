#coding: utf8
"""@package wapi.mall.a_member_waiting_review_products.AMemberWaitingReviewProducts
订单评论列表

"""

#import copy
#from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from business.mall.order_review import OrderReview
from business.mall.review.reviewed_products import ReviewedProducts
import logging
#from core.watchdog.utils import watchdog_info

class AMemberWaitingReviewProducts(api_resource.ApiResource):
	"""
	获取商品的评论列表
	"""
	app = 'member'
	resource = 'waiting_review_products'

	@param_required(['webapp_owner', 'webapp_user'])
	def get(args):
		"""
		得到会员已完成订单中所有未评价的商品列表的订单，
        或者已评价未晒图的订单

		@note 在原Webapp中，get_product_review_list()
		"""


		reviewed_products = ReviewedProducts.get_for_webapp_user({
			'webapp_owner': args['webapp_owner'],
			'webapp_user': args['webapp_user']
			})

		return {
			'reviewed_products': reviewed_products.products
		}
