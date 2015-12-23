#coding: utf8
"""@package wapi.mall.a_member_waiting_review_products.AMemberWaitingReviewProducts
订单评论列表

"""

#import copy
#from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from business.mall.order_review import OrderReview
from business.mall.review.waiting_review_orders import WaitingReviewOrders


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


		waiting_review_orders = WaitingReviewOrders.get_for_webapp_user({
			'webapp_owner': args['webapp_owner'],
			'webapp_user': args['webapp_user']
			})

		orders = waiting_review_orders.orders
		order_list = []

		for order in orders:
			data = {}
			data['order_is_reviewed'] = order.order_is_reviewed
			data['order_id'] = order.order_id
			data['created_at'] = order.created_at
			data['id'] = order.id
			data['final_price'] = order.final_price

			products = []
			for product in order.products:
				product_dict = {}
				product_dict['name'] = product.name
				product_dict['has_picture'] = product.has_reviewed_picture
				product_dict['model'] =  product.model.to_dict() if product.model else {}
				product_dict['product_model_name'] = product.model_name
				product_dict['id'] = product.id
				product_dict['has_review'] = product.has_reviewed
				product_dict['thumbnails_url'] = product.thumbnails_url
				product_dict['order_has_product_id'] = product.rid
				products.append(product_dict)
			data['products'] = products
			order_list.append(data)

		order_list = sorted(order_list, key=lambda x: x['id'], reverse=False)

		return {
			'orders': order_list
		}

