# -*- coding: utf-8 -*-
"""@package business.member.member_factory
订单生成器

"""

import json
from bs4 import BeautifulSoup
import math
import itertools
import uuid
import time
import random
import string
from hashlib import md5
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
# from cache import utils as cache_util
from db.member import models as member_models
#import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
import settings
from business.decorator import cached_context_property
from business.account.member import Member

from business.account.webapp_user import WebAppUser as BusinessWebAppUser


class WebAppUserFactory(business_model.Model):
	"""会员成器
	"""
	__slots__ = (
	)

	@staticmethod
	@param_required(['webapp_owner', 'member_id'])
	def create(args):
		"""工厂方法，创建webapp_user对象

		@return WebappUser对象
		"""
		webapp_user_factory = WebAppUserFactory(args['webapp_owner'], args['member_id'])

		return webapp_user_factory

	def __init__(self, webapp_owner, member_id):
		business_model.Model.__init__(self)
		self.context['webapp_owner'] = webapp_owner
		self.context['member_id'] = member_id

	def save(self):
		"""保存webapp_user信息
		"""
		webapp_owner = self.context['webapp_owner']

		webapp_user = member_models.WebAppUser.create(
			webapp_id = webapp_owner.webapp_id,
			member_id = self.context['member_id']
			)

		return BusinessWebAppUser(webapp_owner, webapp_user)
