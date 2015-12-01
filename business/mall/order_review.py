# -*- coding: utf-8 -*-
"""@package business.mall.order_review
订单评论

原Weapp评论调用的接口是`POST '/webapp/api/project_api/call/'`，其中`target_api`为`product_review/create`。
实际源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
"""

from business import model as business_model
from business.mall.order import Order
from db.mall import models as mall_models
from core.watchdog.utils import watchdog_info
from wapi.decorators import param_required

#import json
#from bs4 import BeautifulSoup
#import math
#from datetime import datetime

#from core.cache import utils as cache_util
#from db.mall import models as mall_models
#from db.mall import promotion_models
#import resource
#from core.watchdog.utils import watchdog_alert

#import settings


class OrderReview(business_model.Model):
	__slots__ = (
		)


	@staticmethod
	@param_required(['order_id', 'owner_id', 'member_id', 'serve_score', 'deliver_score', 'process_score'])
	def create(args):
		"""
		创建订单评论
		"""
		#创建订单评论
		order_review, created = mall_models.OrderReview.objects.get_or_create(
			order_id=args['order_id'],
			owner_id=args['owner_id'],
			member_id=args['member_id'],
			serve_score=args['serve_score'],
			deliver_score=args['deliver_score'],
			process_score=args['process_score'])
		return order_review


	@staticmethod
	def __by_webapp_user_id(args):
		"""
		原mall_models.Order.by_webapp_user_id()

		@see Weapp源码`mall/models.py`中`Order.by_webapp_user_id`

		@todo 需要将这段代码迁移到`business.Order`
		"""
		order_id = args.get('order_id')
		if order_id:
			return mall_models.Order.objects.filter(Q(webapp_user_id__in=webapp_user_id) | Q(id__in=order_id)).filter(origin_order_id__lte=0)
		if isinstance(webapp_user_id, int) or isinstance(webapp_user_id, long):
			return mall_models.Order.objects.filter(webapp_user_id=webapp_user_id, origin_order_id__lte=0)
		else:
			return mall_models.Order.objects.filter(webapp_user_id__in=webapp_user_id, origin_order_id__lte=0)		


	@staticmethod
	@param_required(['orders'])
	def get_order_product_reviews(args):
		"""
		获取订单下商品的评论

		@todo 变量名需要改
		"""
		orders  = args['orders']

		#orderId2orderHasProducts = dict()
		#for orderHasProduct in orderHasProducts:
		#	if not orderId2orderHasProducts.get(orderHasProduct.order_id):
		#		orderId2orderHasProducts[orderHasProduct.order_id] = []
		#	orderId2orderHasProducts.get(orderHasProduct.order_id).append(orderHasProduct)

		#orderHasProductIds = [orderHasProduct.id for orderHasProduct in orderHasProducts]

		# 获取orders全部的product.id
		orderHasProductIds = []
		for order in orders:
			orderHasProductIds.extend([product.id for product in order.products])

		ProductReviews = mall_models.ProductReview.objects.filter(order_has_product_id__in=orderHasProductIds)
		return ProductReviews
	
	@staticmethod
	@param_required([])
	def get_order_product_review_pictures(args):
		"""
		(deprecated)获取订单商品的review picture(改用ProductReview.pictures获取)

		@todo 优化
		"""
		product_reviews = args['product_reviews']
		orderHasProductId2ProductReviews = dict()
		for ProductReview in product_reviews:
			orderHasProductId2ProductReviews[ProductReview.order_has_product_id] = ProductReview

		#allProductReviewPicture = mall_models.ProductReviewPicture.objects.filter(order_has_product_id__in= orderHasProductIds)
		#return allProductReviewPicture
		return []

	@staticmethod
	@param_required(['orders'])
	def __process_with_product_detail(args):
		"""
		处理有商品详情的情况

		@todo  待优化
		"""
		cache_products = webapp_cache.get_webapp_products_detail(request.webapp_owner_id, totalProductIds)
		cache_productId2cache_products = dict([(product.id, product) for product in cache_products])

		# 对于每个订单
		for order in orders:
			products = []             # 订单的所有未评价商品, 或者有评价未晒图
			order_is_reviewed = True  # 订单是否评价完成
			# 对于订单的每件商品
			for orderHasProduct in orderId2orderHasProducts[order.id]:
				# 如果商品有评价
				product_review = orderHasProductId2ProductReviews.get(orderHasProduct.id,False)
				product = copy.copy(cache_productId2cache_products[orderHasProduct.product_id]) #此处需要复制
				if product_review:
					product.has_review = True
					product_review_picture =  _product_review_has_picture(product_review)
					# 如果评价有晒图
					if product_review_picture:
						order_is_reviewed = order_is_reviewed & True
					# 评价无晒图
					else:
						order_is_reviewed = order_is_reviewed & False
						product.order_has_product_id = orderHasProduct.id
						product.has_picture = False
						product.fill_specific_model(
							orderHasProduct.product_model_name, cache_productId2cache_products[product.id].models)
						product.product_model_name = product.custom_model_properties
						products.append(product)
				# 商品无评价
				else:
					order_is_reviewed = order_is_reviewed & False
					product.order_has_product_id = orderHasProduct.id
					product.has_review = False
					product.fill_specific_model(
						orderHasProduct.product_model_name, cache_productId2cache_products[product.id].models)
					product.product_model_name = product.custom_model_properties

					products.append(product)

				product.order_product_model_name = orderHasProduct.product_model_name

			order.products = products
			order.order_is_reviewed = order_is_reviewed


	@staticmethod
	@param_required(['orders'])
	def __process_without_product_detail(args):
		"""
		不需要商品详情的

		@todo 待优化
		"""
		for order in orders:
			order_is_reviewed = True  # 订单是否评价完成
			# 对于订单的每件商品
			for orderHasProduct in orderId2orderHasProducts[order.id]:
				# 如果商品有评价
				product_review = orderHasProductId2ProductReviews.get(orderHasProduct.id,False)
				# product = dict() #此处需要复制
				if product_review:

					product_review_picture =  _product_review_has_picture(product_review)
					# 如果评价有晒图
					if product_review_picture:
						order_is_reviewed = order_is_reviewed & True
					# 评价无晒图
					else:
						order_is_reviewed = order_is_reviewed & False

				# 商品无评价
				else:
					order_is_reviewed = order_is_reviewed & False
			order.order_is_reviewed = order_is_reviewed

	@staticmethod
	@param_required(['webapp_user', 'webapp_owner'])
	def get_order_review_list(args, need_product_detail=False):
		"""
		得到会员已完成订单中所有未评价的商品列表的订单，或者已评价未晒图的订单

			PreCondition: webapp_user_id, member_id,
			PostCondition: orders

		@see 原始代码位置 `webapp/modules/mall/request_util.py`
		"""

		#webapp_user_id = args.webapp_user.id  # 游客身份
		#member_id = args.member.id            # 会员身份
		#member_id = args.webapp_user.member.id

		need_product_detail = args.get('need_product_detail')

		# 得到会员的所有已完成的订单
		#orders = mall_models.Order.by_webapp_user_id(webapp_user_id).filter(status=5)
		orders = Order.get_finished_orders_for_webapp_user({
			'webapp_user': args['webapp_user'],
			'webapp_owner': args['webapp_owner'],
			})
		
		# 获取全部订单id
		# orderIds = [order.id for order in orders]
		#orderHasProducts = OrderHasProduct.objects.filter(order_id__in=orderIds)
		#totalProductIds = [orderHasProduct.product_id for orderHasProduct in orderHasProducts]
		totalProductIds = []
		for order in orders:
			for product in order.products:
				totalProductIds.append(product.id)

		#ProductReviews = mall_models.ProductReview.objects.filter(order_has_product_id__in=orderHasProductIds)
		product_reviews = OrderReview.get_order_product_reviews({
			'orders': orders
			})

		all_product_review_pictures = []
		for product_review in product_reviews:
			all_product_review_pictures.extend(product_review.pictures)

		#ProductReviewPictureIds = [product_review_picture.product_review_id for product_review_picture in all_product_review_pictures]

		if need_product_detail:
			OrderReview.__process_with_product_detail({
				'orders': orders,
				})
		else:
			OrderReview.__process_without_product_detail({
				'orders': orders,
				})
		return orders		