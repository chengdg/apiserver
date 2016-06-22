#coding: utf8
"""@package apimall.a_member_waiting_review_products.AMemberWaitingReviewProducts
订单评论列表

"""

#import copy
#from datetime import datetime

from eaglet.core import api_resource
from eaglet.decorator import param_required
from business.mall.order_review import OrderReview
from business.mall.review.waiting_review_orders import WaitingReviewOrders

from eaglet.utils.resource_client import Resource

import logging
#from eaglet.core import watchdog

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
		param_data = {'woid':args['webapp_owner'].id, 'member_id':args['webapp_user'].member.id }
		get_order_review_json = []
		resp = Resource.use('marketapp_apiserver').get({
				'resource': 'evaluate.get_product_evaluates_status',
				'data': param_data
			})
		if resp:
			code = resp["code"]
			if code == 200:
				get_order_review_json = resp["data"]['orders']

		review2value = {}
		for order_json in get_order_review_json:
			review2value[int(order_json["order_id"])] = order_json["order_is_reviewed"]
			#统计order中评论过的订单的数量，和实际订单中商品的数量作对比，如果不相等则说明订单未评价
			order_product_count = "{}_len".format(order_json["order_id"])
			review2value[order_product_count] = len(order_json["order_product"])
			order_productr_json = order_json["order_product"]
			for product_json in order_productr_json:
				product_id_temp = product_json["order_has_product_id"]
				product_id_temp_review = "{}_{}_review".format(order_json["order_id"],product_id_temp)
				product_id_temp_picture = "{}_{}_picture".format(order_json["order_id"],product_id_temp)

				review2value[product_id_temp_review] = product_json["has_reviewed"]
				review2value[product_id_temp_picture] = product_json["has_reviewed_picture"]


		order_list = []
		for order in orders:
			data = {}
			data['order_is_reviewed'] = order.order_is_reviewed
			order_product_count = "{}_len".format(order.id)
			if review2value.has_key(order.id) and len(order.products)== review2value[order_product_count]:
				data['order_is_reviewed'] = review2value[order.id]
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
				#重新组织从api请求获取到的评论数据
				product_review = "{}_{}_review".format(order.id, product.rid)
				product_picture = "{}_{}_picture".format(order.id, product.rid)
				if review2value.has_key(product_review):
					product_dict['has_review'] = review2value[product_review]
				if review2value.has_key(product_picture):
					product_dict['has_picture'] = review2value[product_picture]
				products.append(product_dict)
			data['products'] = products
			order_list.append(data)

		order_list = sorted(order_list, key=lambda x: x['id'], reverse=False)

		return {
			'orders': order_list
		}

