# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from eaglet.decorator import param_required
# from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from db.account import models as account_models
# import resource
from db.mall import models as mall_models
from db.mall import promotion_models
from db.account import models as account_models
from db.account import weixin_models as weixin_user_models
from db.account import webapp_models as webapp_models
from db.member import models as member_models
import settings
from eaglet.core import watchdog
from core.exceptionutil import unicode_full_stack
from business import model as business_model
import logging


class AccountDivideInfo(business_model.Model):
	"""
	WebApp account_divide_info的信息
	"""
	__slots__ = (
		'id',
		'user_id',
		'settlement_type',
		'divide_rebate',
		'risk_money',
	)
	
	def get_by_owner_id(self, owner_id):
		db_model = account_models.AccountDivideInfo.select().dj_where(user_id=owner_id).first()
		return AccountDivideInfo(db_model)
	
	def __init__(self, db_model):
		business_model.Model.__init__(self)
		if db_model:
			self._init_slot_from_model(db_model)
