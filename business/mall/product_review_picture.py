# -*- coding: utf-8 -*-
"""@package business.mall.product_review
商品评论图片

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


class ProductReviewPicture(business_model.Model):
	__slots__ = (
	)

	@property
	def product_review_id(self):
		"""

		@todo 实现此函数
		"""
		return 0

