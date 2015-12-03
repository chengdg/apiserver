# -*- coding: utf-8 -*-
"""@package business.mall.product_review
商品评论

原Weapp评论调用的接口是`POST '/webapp/api/project_api/call/'`，其中`target_api`为`product_review/create`。
实际源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
"""

from business import model as business_model
from db.mall import models as mall_models

from core.watchdog.utils import watchdog_info
import logging
#import json
#from bs4 import BeautifulSoup
#import math
#from datetime import datetime

from wapi.decorators import param_required
#from core.cache import utils as cache_util
#from db.mall import models as mall_models
#from db.mall import promotion_models
#import resource
#from core.watchdog.utils import watchdog_alert

#import settings


class ProductReview(business_model.Model):
	"""
	商品评价
	"""

	__slots__ = (
		'id',

		'member_id',
		'order_has_product_id',

		'order_review_id',
		'order_id',
		'product_id',
		'product_score',
		'review_detail',
		'created_at',
		'top_name',
		'status',

		#'pictures',
	)


	def __init__(self, model):
		business_model.Model.__init__(self)

		if model:
			self._init_slot_from_model(model)


	@staticmethod
	@param_required(['order_id', 'webapp_owner', 'product_id', 'order_review', 'review_detail', 'product_score', 'member_id', 'order_has_product_id'])
	def create(args):
		"""
		创建商品评论
		"""
		logging.info("to create a ProductReview")
		relation = mall_models.OrderHasProduct.get(id=args['order_has_product_id'])
		model, created = mall_models.ProductReview.get_or_create(
			member_id=args['member_id'],
			order_review=mall_models.OrderReview.get(id=args['order_review'].id),
			order_id=args['order_id'],
			owner_id=args['webapp_owner'].id,
			product_id=args['product_id'],
			order_has_product=relation,
			product_score=args['product_score'],
			review_detail=args['review_detail']
		)
		logging.info("created model, created={}".format(created))
		product_review = ProductReview(model)
		logging.info("product_review={}".format(product_review.to_dict()))

		picture_list = args.get('picture_list')
		if picture_list:
			logging.info("saving product review picture list..., picture_list=%s" % picture_list)
			for picture in list(eval(picture_list)):
				mall_models.ProductReviewPicture(
					product_review=product_review,
					order_has_product_id=args['order_has_product_id'],
					att_url=picture
				).save()
				watchdog_info(u"create_product_review after save img  %s" % (picture), \
					type="mall", user_id=args['owner_id'])
			watchdog_info(u"create_product_review end, order_has_product_id is %s" % \
				(args['order_has_product_id']), type="mall", user_id=args['owner_id'])
		return product_review


	def has_picture(self, product_review, ProductReviewPictureIds):
		"""
		是否有图片

		@see 原始代码位置 `webapp/modules/mall/request_util.py` 
		@todo 只是代码迁移，还未重构
		"""

		def _product_review_has_picture(product_review):
			'''
			评价是否有晒图
			'''
			if product_review.id in ProductReviewPictureIds:
				return True
			else:
				return False
		return _product_review_has_picture(product_review)

	@property
	def pictures(self):
		"""
		获得product review的图片

		@retrun ProductReviewPicture对象list
		@todo 改成缓存
		"""
		#mall_models.ProductReviewPicture.objects.filter(order_has_product_id__in= orderHasProductIds)		
		return []


	@staticmethod
	@param_required(['product_id'])
	def get_latest_product_reviews(args):
		"""
		获得最新limit个商品数量

		@see `mall/module_api.py`中的`get_product_detail_for_cache`。
		"""
		#获取商品的评论
		limit = args.get('limit', 2)
		reviews = mall_models.ProductReview.select().dj_where(
									product_id=args['product_id'],
									status__in=[
										mall_models.PRODUCT_REVIEW_STATUS_PASSED,
										mall_models.PRODUCT_REVIEW_STATUS_PASSED_PINNED
									]).order_by('-top_time', '-id')[:limit]
		#product.product_review = product_review
		product_reviews = [ProductReview(model) for model in reviews]
		return product_reviews
