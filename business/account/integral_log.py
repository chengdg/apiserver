# -*- coding: utf-8 -*-
"""@package business.account.integral_log
会员积分日志
"""

import json
from bs4 import BeautifulSoup
import math
import itertools
import uuid
import time
import random
import string

from wapi.decorators import param_required
from db.member import models as member_models
from business import model as business_model 
import settings
from business.decorator import cached_context_property
from core.watchdog.utils import watchdog_alert, watchdog_warning, watchdog_error
from core.exceptionutil import unicode_full_stack
from business.account.member import Member

SHOPING_REWARDES_IMGE = '/static_v2/img/webapp/usercenter/Shoppingrewards.jpg'
SCAN_REWARDES_IMGE = '/static_v2/img/webapp/usercenter/scanReawards.png'

class IntegralLog(business_model.Model):
	"""
	会员积分日志
	"""
	__slots__ = (
		'id',
		'event_type',
		'integral_count',
		'reason',
		'current_integral',
		'is_friend',
		'created_at',
		'name',
		'pic',
	)

	@staticmethod
	def from_models(query):
		pass

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'model'])
	def from_model(args):
		"""
		工厂对象，根据webapp_owner webapp_user model获取integrallog业务对象

		@param[in] webapp_user
		@param[in] webapp_owner
		@param[in] model: integral model

		@return IntegralLog业务对象
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		model = args['model']

		integral = IntegralLog(webapp_owner, webapp_user, model)
		return integral

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def from_webapp_user(args):
		"""
		工厂对象，根据webapp_owner和webapp_user获取IntegralLog业务对象

		@param[in] webapp_owner
		@param[in] webapp_user

		@return IntegralLog业务对象
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		try:
			integral_db_model = member_models.MemberIntegralLog.get(member_id=webapp_user.member)
			return IntegralLog.from_model({
				'webapp_user': webapp_user,
				'webapp_owner': webapp_owner,
				'model': integral_db_model
			})
		except:
			return None

	def __init__(self, webapp_owner, webapp_user, model):
		business_model.Model.__init__(self)
		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user
		self.context['db_model'] = model

		self._get_current_log_info()


	def _get_current_log_info(self):
		model= self.context['db_model']
		webapp_owner = self.context['webapp_owner']
		if model.follower_member_token:
			token = model.follower_member_token
			follower_member = Member.from_token({
					'webapp_owner': webapp_owner,
					'token': model.follower_member_token
				})
		else:
			follower_member = None
		self.id = model.id
		self.event_type = model.event_type
		self.created_at = model.created_at
		self.integral_count = model.integral_count
		self.reason = model.reason
		self.current_integral = model.current_integral

		self.is_friend = False
		if u'好友' in self.event_type or u'推荐扫码' in self.event_type:
			self.is_friend = True
			if follower_member and friend_member.user_icon and friend_member.user_icon != '':
				self.pic = friend_member.user_icon
				self.name = friend_member.username_size_ten
			else:
				self.pic = SCAN_REWARDES_IMGE
				self.name = ''

		elif u'购物返利' in self.event_type or u'评' in self.event_type or self.event_type == u'活动奖励':
			self.pic = SHOPING_REWARDES_IMGE
			self.name = ''
		else:
			self.pic = SCAN_REWARDES_IMGE
			self.name = ''

