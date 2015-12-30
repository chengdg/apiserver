# -*- coding: utf-8 -*-
"""@package business.mall.express.express_detail
表示快递(物流)一条详情信息

"""

#import json
#from bs4 import BeautifulSoup
#import math
#import itertools

#from wapi.decorators import param_required
#from wapi import wapi_utils
#from core.cache import utils as cache_util
#from db.mall import models as mall_models
#from core.watchdog.utils import watchdog_alert
from business import model as business_model 
#from business.mall.review.waiting_review_order import WaitingReviewOrder
#from business.mall.order import Order
#import settings


class ExpressDetail(business_model.Model):
	"""
	一条物流详情

	@see Weapp的`weapp/mall/models.py`中的`get_express_details()`
	
	@see Weapp的`weapp/tools/express/util.py`中的`get_express_details_by_order`
	"""
	__slots__ = (
		'id',
		'express_id',
		'status',
		'time',
		'ftime',
		'display_index',
		'created_at',

		'context',
	)

	def __init__(self, model = None):
		business_model.Model.__init__(self)
		if model:
			self._init_slot_from_model(model)
	
	@property
	def content(self):
		return self.context
