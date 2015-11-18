# -*- coding: utf-8 -*-

"""会员
"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
from wapi.mall import promotion_models
from wapi.member import models as member_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model
import settings
from business.decorator import cached_context_property
from utils import emojicons_util

class Member(business_model.Model):
	"""会员
	"""
	__slots__ = (
		'grade_id',
		'username_hexstr'
	)

	@staticmethod
	def from_models(query):
		pass

	@staticmethod
	def from_model(webapp_owner, model):
		member = Member(webapp_owner, model)
		member._init_slot_from_model(model)

		return member

	@staticmethod
	def from_id(member_id, webapp_owner):
		try:
			member_db_model = member_models.Member.get(id=member_id)
			return Member.from_model(member_db_model, webapp_owner)
		except:
			return None

	def __init__(self, webapp_owner, model):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['db_model'] = model

	@property
	def discount(self):
		"""
		[property] 会员折扣
		"""
		member_model = self.context['db_model']
		if not member_model:
			return -1, 100

		member_grade = self.__grade
		if member_grade:
			return member_model.grade_id, member_grade.shop_discount
		else:
			return member_model.grade_id, 100

	@cached_context_property
	def __grade(self):
		"""
		[property] 会员等级信息
		"""
		member_model = self.context['db_model']
		webapp_owner = self.context['webapp_owner']

		if not member_model:
			return None

		member_grade_id = member_model.grade_id
		member_grade = webapp_owner.member2grade.get(member_grade_id, '')
		return member_grade

	@cached_context_property
	def integral_info(self):
		"""
		积分信息
		"""
		member_model = self.context['db_model']
		if member_model:
			count = member_model.integral
			grade = self.__grade
			if grade:
				usable_integral_percentage_in_order = grade.usable_integral_percentage_in_order
			else:
				usable_integral_percentage_in_order = 100
		else:
			count = 0
			usable_integral_percentage_in_order = 100

		integral_strategy_settings = self.context['webapp_owner'].integral_strategy_settings
		return {
			'count': count,
			'count_per_yuan': integral_strategy_settings.integral_each_yuan,
			'usable_integral_percentage_in_order' : usable_integral_percentage_in_order,
			'usable_integral_or_conpon' : integral_strategy_settings.usable_integral_or_conpon
		}

	@cached_context_property
	def username_for_html(self):
		if (self.username_hexstr is not None) and (len(self.username_hexstr) > 0):
			username = emojicons_util.encode_emojicons_for_html(self.username_hexstr, is_hex_str=True)
		else:
			username = emojicons_util.encode_emojicons_for_html(self.username)		

		try:
			username.decode('utf-8')
		except:
			username = self.username_hexstr

		return username