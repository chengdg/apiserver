# -*- coding: utf-8 -*-
"""@package business.account.member
会员
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
from db.member import models as member_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model
import settings
from business.decorator import cached_context_property
from utils import emojicons_util
from business.account.member_order_info import MemberOrderInfo


class SocialAccount(business_model.Model):
	"""
	SocialAccount，社会化帐号
	"""
	__slots__ = (
		'id',
		'openid',
		'webapp_id',
	)

	@staticmethod
	def from_models(query):
		pass

	@staticmethod
	@param_required(['webapp_owner', 'model'])
	def from_model(args):
		"""
		SocialAccount model获取SocialAccount业务对象

		@param[in] webapp_owner
		@param[in] model: SocialAccount model

		@return SocialAccount业务对象
		"""
		webapp_owner = args['webapp_owner']
		model = args['model']

		social_account = SocialAccount(webapp_owner, model)
		social_account._init_slot_from_model(model)
		return social_account

	@staticmethod
	@param_required(['webapp_owner', 'id'])
	def from_id(args):
		"""
		工厂对象，根据member id获取Member业务对象

		@param[in] webapp_owner
		@param[in] id: SC的id

		@return Member业务对象
		"""
		webapp_owner = args['webapp_owner']
		id = args['id']
		try:
			member_db_model = member_models.SocialAccount.get(id=id)
			return SocialAccount.from_model({
				'webapp_owner': webapp_owner,
				'model': member_db_model
			})
		except:
			return None

	@staticmethod
	@param_required(['webapp_owner', 'openid'])
	def from_openid(args):
		"""
		工厂对象，根据opend_id获取Member业务对象

		@param[in] webapp_owner
		@param[in] openid: 会员的openid

		@return SocialAccount对象
		"""
		webapp_owner = args['webapp_owner']
		openid = args['openid']
		#try:
		member_db_model = member_models.SocialAccount.get(webapp_id=webapp_owner.webapp_id,openid=openid)
		return SocialAccount.from_model({
			'webapp_owner': webapp_owner,
			'model': member_db_model
		})
		#except:
		#	return None	

	def __init__(self, webapp_owner, model):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['db_model'] = model

	@staticmethod
	def empty_social_account():
		"""工厂方法，创建空的social_account对象

		@return SocialAccount对象
		"""
		social_account = SocialAccount(None, None)
		return social_account


	@staticmethod
	@param_required(['webapp_owner', 'member_id'])
	def from_member_id(args):
		"""
		工厂对象，根据member id获取Member业务对象

		@param[in] webapp_owner
		@param[in] member_id: SC的id

		@return Member业务对象
		"""
		webapp_owner = args['webapp_owner']
		member_id = args['member_id']
		try:
			member_db_model = member_models.MemberHasSocialAccount.select().dj_where(member_id=member_id).first().account
			return SocialAccount.from_model({
				'webapp_owner': webapp_owner,
				'model': member_db_model
			})
		except:
			return None


