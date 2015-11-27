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

#from wapi.decorators import param_required
#from core.cache import utils as cache_util
#from db.mall import models as mall_models
#from db.mall import promotion_models
#import resource
#from core.watchdog.utils import watchdog_alert

#import settings


class ProductReview(business_model.Model):
	__slots__ = (
		)


	@staticmethod
	def create(order_id, owner_id, product_id, order_review, review_detail, product_score, member_id, order_has_product_id, picture_list):
		"""
		创建商品评论
		"""
		product_review, created = mall_models.ProductReview.objects.get_or_create(
			member_id=member_id,
			order_review=order_review,
			order_id=order_id,
			owner_id=owner_id,
			product_id=product_id,
			order_has_product_id=order_has_product_id,
			product_score=product_score,
			review_detail=review_detail
		)

		if picture_list:
			for picture in list(eval(picture_list)):
				mall_models.ProductReviewPicture(
					product_review=product_review,
					order_has_product_id=order_has_product_id,
					att_url=picture
				).save()
				watchdog_info(u"create_product_review after save img  %s" % (picture), \
					type="mall", user_id=owner_id)
			watchdog_info(u"create_product_review end, order_has_product_id is %s" %\
				(order_has_product_id), type="mall", user_id=owner_id)
		return
