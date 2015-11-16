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
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model
import settings


class Member(business_model.Model):
	"""会员
	"""
	__slots__ = (
		'grade_id',
	)

	@staticmethod
	def from_models(query):
		pass

	@staticmethod
	def from_model(model, webapp_owner):
		member = Member(webapp_owner, model)
		member._init_slot_from_model(model)

		return member

	def __init__(self, webapp_owner, model):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['member'] = model

	@property
	def discount(self):
		member_model = self.context['member']
		webapp_owner = self.context['webapp_owner']

		if not member_model:
			return -1, 100

		member_grade_id = member_model.grade_id
		member_grade = webapp_owner.member2grade.get(member_grade_id, '')
		if member_grade:
			return member_grade_id, member_grade.shop_discount
		else:
			return member_grade_id, 100
