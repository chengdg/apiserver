# -*- coding: utf-8 -*-
"""@package business.mall.order_review
订单评论

原Weapp评论调用的接口是`POST '/webapp/api/project_api/call/'`，其中`target_api`为`product_review/create`。
实际源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
"""

from business import model as business_model
from db.mall import models as mall_models
from core.watchdog.utils import watchdog_info


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


class OrderReview(business_model.Model):
	__slots__ = (
		)

	@staticmethod
	def create(order_id, owner_id, member_id, serve_score, deliver_score, process_score):
		"""
		创建订单评论
		"""
		#创建订单评论
		order_review, created = mall_models.OrderReview.objects.get_or_create(
			order_id=order_id,
			owner_id=owner_id,
			member_id=member_id,
			serve_score=serve_score,
			deliver_score=deliver_score,
			process_score=process_score)
		return
