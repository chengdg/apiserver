# -*- coding: utf-8 -*-
"""@package business.account.member_info_updater
会员信息定时更新器

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

class MemberInfoUpdater(business_model.Model):
	"""会员信息定时更新器
	"""
	__slots__ = ()

	def __init__(self, webapp_owner):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner

	def update(member):
		"""更新会员信息

		每天更新一次，处理以下情况：
			1. 会员更改昵称
			2. 会员取消关注
		"""
		print 'TODO2: update member info'