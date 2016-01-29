# -*- coding: utf-8 -*-
"""@package business.mall.promotion.promotion_result
促销结果，每一次应用促销都会获得一个促销结果

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
#from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from core.watchdog.utils import watchdog_alert
from business import model as business_model
import settings


class PromotionResult(business_model.Model):
	"""
	促销结果
	"""
	__slots__ = (
		'version',
		'is_success',
		'saved_money', #促销优惠价格
		'subtotal', #promotion product group应用促销后的金额小记
		'need_disable_discount', #促销是否禁用会员折扣
		'detail', #与具体促销相关的细节信息
		'updated_premium_products'  # 已更新库存的赠品
	)

	def __init__(self, saved_money=0, subtotal=0, detail=None):
		business_model.Model.__init__(self)

		self.version = settings.PROMOTION_RESULT_VERSION
		self.is_success = True
		self.saved_money = saved_money
		self.subtotal = subtotal
		self.need_disable_discount = False
		self.updated_premium_products = []
		if detail:
			self.detail = detail

	def to_dict(self):
		result = {
			'version': self.version,
			'saved_money': self.saved_money,
			'promotion_saved_money': self.saved_money,  #为了兼容weapp后端系统，此字段在apiserver中无用
			'subtotal': self.subtotal
		}
		if self.detail:
			result.update(self.detail)

		return result