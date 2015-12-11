# -*- coding: utf-8 -*-
"""@package business.inegral_allocator.IntegralResourceAllocator
请求积分资源

"""
import logging
import json
from bs4 import BeautifulSoup
import math
import itertools
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.account.integral import Integral

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
			return True, u'积分不足'
		else:
			successed, integral_log_id = webapp_user.use_integral(integral)
			self.integral_log_id = integral_log_id
			if successed:
				return True, ''
			else:
				return False, u'扣除积分失败'

	@cached_context_property
	def money(self):
		webapp_owner = self.context['webapp_owner']
		count_per_yuan = webapp_owner.integral_strategy_settings.integral_each_yuan

		integral_money = round(float(count_per_yuan*self.integral), 2)
		return integral_money

