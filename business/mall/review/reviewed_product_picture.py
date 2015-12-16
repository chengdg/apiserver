# -*- coding: utf-8 -*-
"""@package business.mall.review.reviewed_product.ReviewedProductPicture
	商品评价对象ReviewedProduct的图片ReviewedProductPicture对象
"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils

from db.mall import models as mall_models

import resource
import settings
from core.watchdog.utils import watchdog_alert
from core.cache import utils as cache_util
from utils import emojicons_util

from business import model as business_model

class ReviewedProductPicture(business_model.Model):
	"""
	商品评价对象ReviewedProduct的图片ReviewedProductPicture对象
	"""
	__slots__ = (
		'id',
		'att_url'
	)

	@staticmethod
	@param_required(['model'])
	def from_model(args):
		"""
		工厂对象，根据ProductReview model获取ReviewedProduct业务对象

		@param[in] model: ProductReviewPicture model

		@return ReviewedProductPicture业务对象
		"""
		model = args['model']

		reviewed_product_picture = ReviewedProductPicture(model)
		reviewed_product_picture._init_slot_from_model(model)
		return reviewed_product_picture



	def __init__(self, model):
		business_model.Model.__init__(self)
		self.context['db_model'] = model

