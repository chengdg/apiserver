# -*- coding: utf-8 -*-
"""@package wapi.member.a_member_review_product.AMemberReviewProduct
评论API

"""
import time

from core import api_resource
from wapi.decorators import param_required
from business.mall.order_review import OrderReview
from business.mall.review.review_product_factory import ReviewProductFactory
from business.mall.review.review_order_factory import ReviewOrderFactory
from business.mall.review.reviewed_order import ReviewedOrder
from business.mall.review.reviewed_product import ReviewedProduct
from business.mall.review.waiting_review_orders import WaitingReviewOrders
from business.mall.order_products import OrderProducts

from business.mall.product import Product
from business.mall.order import Order

import logging

#from core.watchdog.utils import watchdog_info


class AMemberReviewProduct(api_resource.ApiResource):
	"""
	会员评论商品

	@see 原始源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
	"""
	app = 'member'
	resource = 'review_product'



	@param_required(['webapp_owner', 'webapp_user', 'order_id', 'product_id', 'order_has_product_id'])
	def put(args):
		"""
		创建评论

		@param order_id
		@param product_id
		@param order_has_product_id
		@param [IN] send_time
		@param [IN] detail_time

		@see 原始代码为Weapp的`create_product_review()`
		"""
		picture_list = args.get('picture_list')

		# 从`webapp/modules/mall/request_api_utils.py:create_product_review()`中迁移
		# 规格化所需数据
		#owner_id = int(request.webapp_owner_id)
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		order_id = args['order_id']
		#member_id = int(request.member.id)
		member = webapp_user.member
		member_id = member.id
		product_id = int(args['product_id'])
		order_has_product_id = int(args['order_has_product_id'])

		send_time = args.get('send_time', None)
		# 原来是`detal_time`(by Victor)
		detail_time = args.get('detail_time', None)

		#request_length = request.META['CONTENT_LENGTH']

		if send_time and detail_time:
			send_time = float(send_time)
			detail_time = float(detail_time)
			send_time = send_time + detail_time
			total_seconds =  time.time() - send_time
			logging.info(u"order_has_product_id: %d, request time: %d, response time: %d, total_seconds: %d, total_size: %dkb" %
							(order_has_product_id, float(send_time), time.time(), total_seconds, int(request_length)//1024),
					  type="mall",
					  user_id=int(webapp_owner.id))

		product_score = args.get('product_score', None)
		review_detail = args.get('review_detail', None)
		serve_score = args.get('serve_score', None)
		deliver_score = args.get('deliver_score', None)
		process_score = args.get('process_score', None)
		picture_list = args.get('picture_list', None)
		

		if len(review_detail) == 0 or len(review_detail) > 200:
			return {'status': 0, 'errmsg': 'error detail length'}
		# 由业务模型创建review
		order_review = ReviewedOrder.get_from_order_id({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user,
			'order_id': order_id
			})
		if not order_review:
			order_review = ReviewOrderFactory.create({
				'webapp_owner': webapp_owner,
				'webapp_user': webapp_user,
				'order_id': order_id,
				'serve_score': serve_score,
				'deliver_score': deliver_score,
				'process_score': process_score}).save()

		# 创建商品评论
		product_review = ReviewedProduct.from_order_has_product_id({
			'order_has_product_id': order_has_product_id,
			'webapp_owner': webapp_owner,
			})

		if not product_review:
			product_review = ReviewProductFactory.create({
				'webapp_owner': webapp_owner,
				'webapp_user': webapp_user,
				'order_id':order_id,
				'product_id':product_id,
				'order_review_id':order_review.id,
				'review_detail':review_detail,
				'product_score':product_score,
				'order_has_product_id':order_has_product_id,
				'picture_list':picture_list
				}).save()

		#请求是否还有待评价商品
		waiting_review_orders = WaitingReviewOrders.get_for_webapp_user({
			'webapp_owner': args['webapp_owner'],
			'webapp_user': args['webapp_user']
			})

		orders = waiting_review_orders.orders
		order_list = []
		has_waiting_review = False
		for order in orders:
			if  order.order_is_reviewed is False:
				has_waiting_review = True
				break

			for product in order.products:
				if product.has_reviewed is False:
					has_waiting_review = True
					break

				if product.has_reviewed_picture is False:
					has_waiting_review = True
					break

			if has_waiting_review:
				break

		return {'status': 1, 'errmsg': '', 'has_waiting_review': 1 if has_waiting_review else 0}


	@param_required(['webapp_owner', 'webapp_user', 'order_id', 'product_id', 'order_has_product_id'])
	def get(args):
		"""
		获得评论信息
		"""
		#owner_id = int(request.webapp_owner_id)
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		owner_id = webapp_user.id
		order_id = args['order_id']
		#member_id = int(request.member.id)
		member = webapp_user.member
		member_id = member.id
		product_id = int(args['product_id'])
		order_has_product_id = int(args['order_has_product_id'])


		send_time = time.time()
		
		# product = Product.from_id({
		# 	"webapp_owner": webapp_owner,
		# 	"member": webapp_user.member,
		# 	"product_id": product_id
		# }).to_dict()
		
		order = Order.from_id({
			'webapp_owner': webapp_user,
			'webapp_user': webapp_owner,
			'order_id': order_id
		})

		order_products = OrderProducts.get_for_order({
				'webapp_owner': webapp_owner,
				'webapp_user': webapp_user,
				'order': order
			})

		products = order_products.products

		product = {}

		for p in products:
			if p.id == product_id:
				product = p.to_dict()
				break

		product_review = ReviewedProduct.from_order_has_product_id({
			'order_has_product_id': order_has_product_id,
			'webapp_owner': webapp_owner
			})

		reviewed_product = {}
		if product_review:
			reviewed_product['id'] = product_review.id
			reviewed_product['product_score'] = product_review.product_score
			reviewed_product['review_detail'] = product_review.review_detail
			reviewed_product['reviewed_product_pictures'] = product_review.reviewed_product_pictures


		return {
			'order_has_product_id': order_has_product_id,
			'order_id': order_id,
			'product': product,
			'reviewed_product': reviewed_product,
			'send_time': send_time
		}


	@param_required(['webapp_owner', 'webapp_user', 'order_id', 'product_id', 'order_has_product_id', 'picture_list'])
	def post(args):
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		order_id = args['order_id']
		#member_id = int(request.member.id)
		member = webapp_user.member
		member_id = member.id
		product_id = int(args['product_id'])
		order_has_product_id = int(args['order_has_product_id'])
		picture_list = args['picture_list']

		order_review = ReviewedOrder.get_from_order_id({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user,
			'order_id': order_id
			})

		if order_review:
			product_review = ReviewedProduct.from_order_has_product_id({
				'order_has_product_id': order_has_product_id,
				'webapp_owner': webapp_owner,
				})
			if product_review and not product_review.reviewed_product_pictures:
				ReviewProductFactory.create_reviewed_product_pictures({
					'reviewed_id': product_review.id,
					'pictures': picture_list,
					'order_has_product_id': order_has_product_id
					})

		#请求是否还有待评价商品
		waiting_review_orders = WaitingReviewOrders.get_for_webapp_user({
			'webapp_owner': args['webapp_owner'],
			'webapp_user': args['webapp_user']
			})

		orders = waiting_review_orders.orders
		order_list = []
		has_waiting_review = False
		for order in orders:
			if  order.order_is_reviewed is False:
				has_waiting_review = True
				break

			for product in order.products:
				if product.has_reviewed is False:
					has_waiting_review = True
					break

				if product.has_reviewed_picture is False:
					has_waiting_review = True
					break

			if has_waiting_review:
				break

		return {'status': 1, 'errmsg': '', 'has_waiting_review': 1 if has_waiting_review else 0}




