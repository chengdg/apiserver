# -*- coding: utf-8 -*-
"""@package business.resource.integral_resource
积分资源

积分资源的属性：

属性	| 类型	| 说明
:------   | :------- | :-------
integral | 数值	| 积分数量
money  | 数值 	| 表示积分对应的价格
integral_log_id	| 数值	| 积分记录ID(待确认)
"""

import logging
import decimal
#import json
#from bs4 import BeautifulSoup
#import math
#import itertools
#from datetime import datetime

from eaglet.decorator import param_required
##from wapi import wapi_utils
#from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from eaglet.core import watchdog
from business import model as business_model
#from business.mall.product import Product
#import settings
from business.decorator import cached_context_property
#from business.account.integral import Integral

class IntegralResource(business_model.Resource):
	"""积分资源
	"""
	__slots__ = (
		'type',
		'integral',
		'money',
		'integral_log_id'
		)


	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'type'])
	def get(args):
		"""工厂方法，创建IntegralResource对象

		@return IntegralResource对象
		"""
		integral_resource = IntegralResource(args['webapp_owner'], args['webapp_user'], args['type'])

		return integral_resource

	def __init__(self, webapp_owner, webapp_user, type):
		business_model.Resource.__init__(self)
		self.type = type
		self.context['webapp_user'] = webapp_user
		self.context['webapp_owner'] = webapp_owner
		self.context['money'] = None

	def get_type(self):
		return self.type

	def get_resource(self, integral):
		self.integral = integral
		#self.money = integral_money
		webapp_user = self.context['webapp_user']
		self.integral_log_id = -1
		if integral > 0 and not webapp_user.can_use_integral(integral):
			return False, u'积分不足'
		elif integral == 0:
			return True, u'00'
		else:
			successed, integral_log_id = webapp_user.use_integral(integral)
			self.integral_log_id = integral_log_id
			if successed:
				return True, ''
			else:
				return False, u'扣除积分失败'

	@property
	def money(self):
		if self.context['money']:
			return self.context['money']
		else:
			webapp_owner = self.context['webapp_owner']
			count_per_yuan = webapp_owner.integral_strategy_settings.integral_each_yuan

			if count_per_yuan == 0:
				logging.error("ERROR: count_per_yuan SHOULD NOT be ZERO!")
				integral_money = float(self.integral)
			else:
				integral_money = float(float(self.integral)/count_per_yuan)
			integral_money = decimal.Decimal(integral_money).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_05UP)

			return float(integral_money)

	@money.setter
	def money(self, money):
		self.context['money'] = money
