# -*- coding: utf-8 -*-
"""@package wapi.member.a_member_review_product.AMemberReviewProduct
评论API

"""

from core import api_resource
from wapi.decorators import param_required
from business.mall.order_review import OrderReview
from business.mall.review.review_product_factory import ReviewProductFactory
from business.mall.review.review_order_factory import ReviewOrderFactory
import logging

#from core.watchdog.utils import watchdog_info


class AMemberReviewProduct(api_resource.ApiResource):
	"""
	会员评论商品

	@see 原始源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
	"""
	app = 'member'
	resource = 'review_product'

	# @staticmethod
	# def _get_review_status(request):
	# 	"""
	# 	得到个人中心待评价列表的状态，
	# 	如果所有订单已完成晒图， 返回True
	# 	否则返回 False

	# 	@todo 待优化
	# 	"""
	# 	# 得到个人中心的所用订单
	# 	#orders = request_util._get_order_review_list(request)
	# 	orders = OrderReview.get_order_review_list(request)
	# 	# 如果订单都已经完成晒图
	# 	result = True
	# 	for order in orders:
	# 		result = result & order.order_is_reviewed
	# 	return result


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
		owner_id = webapp_user.id
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
		#创建订单评论
		"""
		order_review, created = mall_models.OrderReview.objects.get_or_create(
			order_id=order_id,
			owner_id=owner_id,
			member_id=member_id,
			serve_score=serve_score,
			deliver_score=deliver_score,
			process_score=process_score)
		"""
		# 由业务模型创建review
		order_review = ReviewOrderFactory.create({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user,
			'order_id': order_id,
			'owner_id': owner_id,
			'member_id': member_id,
			'serve_score': serve_score,
			'deliver_score': deliver_score,
			'process_score': process_score}).save()

		# 创建商品评论
		product_review = ReviewProductFactory.create({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user,
			'order_id':order_id,
			#'owner_id':owner_id,
			'product_id':product_id,
			'order_review_id':order_review.id,
			'review_detail':review_detail,
			'product_score':product_score,
			'member_id':member_id,
			'order_has_product_id':order_has_product_id,
			'picture_list':picture_list
			}).save()

		#response = create_response(200)
		#response.data = get_review_status(request)
		#data = AReview._get_review_status(args)
		return {}


	# @param_required([])
	# def get(args):
	# 	"""
	# 	获得评论信息
	# 	"""
	# 	return {
	# 	}
