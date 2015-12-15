# -*- coding: utf-8 -*-
"""@package business.mall.promotion.promotion_result
促销结果

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from core.watchdog.utils import watchdog_alert
from business import model as business_model
import settings
from business.mall.promotion.promotion_result import PromotionResult


class PromotionFailure(PromotionResult):
	"""
	促销失败
	"""
	__slots__ = (
		'type', #失败类型
		'msg', #失败信息
		'short_msg', #失败信息简版

		'id',
		'name',
		'stocks',
		'model_name',
		'pic_url'
	)

	def __init__(self, options):
		PromotionResult.__init__(self, 0, 0)
		self.is_success = False
		self.type = options['type']
		self.msg = options['msg']
		self.short_msg = options['short_msg']

	def to_dict(self):
		result = {}
		for slot in PromotionFailure.__slots__:
			result[slot] = getattr(self, slot, None)

		return result