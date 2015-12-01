# -*- coding: utf-8 -*-
"""@package business.mall.order_review
订单评论

原Weapp评论调用的接口是`POST '/webapp/api/project_api/call/'`，其中`target_api`为`product_review/create`。
实际源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
"""

from business import model as business_model
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
	def get_order_review_list(request,need_product_detail=False):
		'''
		得到会员已完成订单中所有未评价的商品列表的订单，或者已评价未晒图的订单

			PreCondition: webapp_user_id, member_id,
			PostCondition: orders

		@see 原始代码位置 `webapp/modules/mall/request_util.py`
		'''

		webapp_user_id = request.webapp_user.id  # 游客身份
		member_id = request.member.id            # 会员身份

		# 得到会员的所有已完成的订单
		orders = Order.by_webapp_user_id(webapp_user_id).filter(status=5)
		orderIds = [order.id for order in orders]
		orderHasProducts = OrderHasProduct.objects.filter(order_id__in=orderIds)
		totalProductIds = [orderHasProduct.product_id for orderHasProduct in orderHasProducts]

		orderId2orderHasProducts = dict()
		for orderHasProduct in orderHasProducts:
			if not orderId2orderHasProducts.get(orderHasProduct.order_id):
				orderId2orderHasProducts[orderHasProduct.order_id] = []
			orderId2orderHasProducts.get(orderHasProduct.order_id).append(orderHasProduct)

		orderHasProductIds = [orderHasProduct.id for orderHasProduct in orderHasProducts]
		ProductReviews = mall_models.ProductReview.objects.filter(order_has_product_id__in=orderHasProductIds)
		orderHasProductId2ProductReviews = dict()
		for ProductReview in ProductReviews:
			orderHasProductId2ProductReviews[ProductReview.order_has_product_id] = ProductReview

		allProductReviewPicture = mall_models.ProductReviewPicture.objects.filter(order_has_product_id__in= orderHasProductIds)
		ProductReviewPictureIds = [ProductReviewPicture.product_review_id for ProductReviewPicture in allProductReviewPicture]
		def _product_review_has_picture(product_review):
			'''
			评价是否有晒图
			'''


			if product_review.id in ProductReviewPictureIds:
				return True
			else:
				return False

		if need_product_detail:
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
		else:
			##############################################################################
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

		return orders		