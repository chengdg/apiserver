# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup
from datetime import timedelta

from core import inner_resource
from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from wapi.mall import models as mall_models
import settings

OVERDUE_DAYS = 15

class RTopProductReview(inner_resource.Resource):
	"""
	商品详情
	"""
	app = 'mall'
	resource = 'top_product_review'

	@param_required(['product_id'])
	def post(args):
		product_id = args['product_id']
		top_review_list = mall_models.ProductReview.select().dj_where(status=2, product_id=product_id)
		for review in top_review_list:
			after_15_days = review.top_time + timedelta(days=OVERDUE_DAYS)
			now = datetime.now()
			if (after_15_days <= now):
				review.status = 1
				mall_models.ProductReview.update(status=1, top_time=DEFAULT_DATETIME).dj_where(id=review.id)

