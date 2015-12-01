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
	__slots__ = (
		'pictures',
		)


	@staticmethod
	@param_required(['order_id', 'owner_id', 'product_id', 'order_review', 'review_detail', 'product_score', 'member_id', 'order_has_product_id'])
	def create(args):
		"""
		创建商品评论
		"""
		product_review, created = mall_models.ProductReview.objects.get_or_create(
			member_id=args['member_id'],
			order_review=args['order_review'],
			order_id=args['order_id'],
			owner_id=args['owner_id'],
			product_id=args['product_id'],
			order_has_product_id=args['order_has_product_id'],
			product_score=args['product_score'],
			review_detail=args['review_detail']
		)

		picture_list = args.get('picture_list')
		if picture_list:
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
		return


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

