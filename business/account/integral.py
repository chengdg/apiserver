# -*- coding: utf-8 -*-
"""@package business.spread

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

class Integral(business_model.Model):
	"""
	会员积分
	"""
	__slots__ = (
		'id',
		'click_shared_url_increase_count',
		'be_member_increase_count',
		'buy_award_count_for_buyer',
		'buy_via_shared_url_increase_count_for_author',
		'buy_via_offline_increase_count_for_author',
		'webapp_id',
	)

	@staticmethod
	def from_models(query):
		pass

	@staticmethod
	@param_required(['webapp_owner', 'model'])
	def from_model(args):
		"""
		工厂对象，根据member model获取integral业务对象

		@param[in] webapp_owner
		@param[in] model: integral model

		@return Member业务对象
		"""
		webapp_owner = args['webapp_owner']
		model = args['model']

		integral = Integral(webapp_owner, model)
		integral._init_slot_from_model(model)
		return integral

	@staticmethod
	@param_required(['webapp_owner'])
	def from_webapp_id(args):
		"""
		工厂对象，根据Integral id获取Integral业务对象

		@param[in] webapp_owner

		@return Integral业务对象
		"""
		webapp_owner = args['webapp_owner']
		try:
			integral_db_model = member_models.IntegralStrategySttings.get(webapp_id=webapp_owner.webapp_id)
			return Integral.from_model({
				'webapp_owner': webapp_owner,
				'model': integral_db_model
			})
		except:
			return None

	def __init__(self, webapp_owner, model):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['db_model'] = model

	@staticmethod
	@param_required(['member', 'follower_member', 'click_shared_url_increase_count'])
	def increase_click_shared_url_count(args):
		args['event_type'] = member_models.FOLLOWER_CLICK_SHARED_URL
		args['integral_increase_count'] = args['click_shared_url_increase_count']
		Integral.increase_member_integral(args)

	@staticmethod
	def increase_member_integral(args):
		member = args['member']
		event_type = args['event_type']
		integral_increase_count = args.get('integral_increase_count', 0)
		follower_member = args.get('follower_member', None)
		reason = args.get('reason', '')
		manager = args.get('manager', '')
		webapp_user = args.get('webapp_user', None)

		integral_increase_count = int(integral_increase_count)

		if integral_increase_count == 0:
			return None

		if webapp_user:
			webapp_user_id = webapp_user.id
		else:
			webapp_user_id = 0
		current_integral = member.integral + integral_increase_count
		try:
			#TODO-bert 并发下是否会出现积分日志无法对应上
			member_models.Member.update(integral=member_models.Member.integral + integral_increase_count).dj_where(id=member.id).execute()

			integral_log = member_models.MemberIntegralLog.create(
					member = member.id, 
					follower_member_token = follower_member.token if follower_member else '', 
					integral_count = integral_increase_count, 
					event_type = event_type,
					webapp_user_id = webapp_user_id,
					reason=reason,
					current_integral=current_integral,
					manager=manager
				)
			if webapp_user:
				webapp_user.cleanup_cache

			return True, integral_log.id
		except:
			notify_message = u"update_member_integral member_id:{}, cause:\n{}".format(member.id, unicode_full_stack())
			watchdog_error(notify_message)
			return False, None
		

	@staticmethod
	def use_integral_to_buy(args):
		webapp_user = args['webapp_user']
		use_count = int(args['integral_count'])

		if use_count == 0:
			return True, None

		return Integral.increase_member_integral({
			'integral_increase_count': use_count,
			'member': webapp_user.member,
			'event_type':  member_models.USE
			})
		
	@staticmethod
	def roll_back_integral(args):
		webapp_user = args['webapp_user']
		integral_log_id = args['integral_log_id']
		integral_count = args['integral_count']
		#TODO-bert 增加watchdog
		member_models.Member.update(integral=member_models.Member.integral + integral_count).dj_where(id=webapp_user.member.id).execute()
		member_models.MemberIntegralLog.delete().dj_where(id=integral_log_id)
