# -*- coding: utf-8 -*-
"""@package business.account.integral_logs
积分日子集合

"""

import json
from bs4 import BeautifulSoup
import math
import itertools

from eaglet.decorator import param_required
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from db.member import models as member_models
from eaglet.core import watchdog
from business import model as business_model 
from business.mall.order_product import OrderProduct 
from business.mall.forbidden_coupon_product_ids import ForbiddenCouponProductIds
from business.account.integral_log import IntegralLog 
from util import dateutil


class IntegralLogs(business_model.Model):
	"""积分日志集合
	"""
	__slots__ = (
		'integral_logs',
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def get(args):
		"""工厂方法，创建IntegralLogs对象

		@param[in] webapp_owner
		@param[in] webapp_user

		@return IntegralLogs对象
		"""
		integral_logs = IntegralLogs(args['webapp_owner'], args['webapp_user'])
		integral_logs.__get_integral_logs()

		return integral_logs


	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

	
	def __get_integral_logs(self):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user'] 
		integral_logs_list = []
		integral_logs = member_models.MemberIntegralLog.select().dj_where(member_id=webapp_user.member.id).order_by(-member_models.MemberIntegralLog.created_at)

		followers_token = []
		followers_token2member = {}

		# 将所有涉及好友分享的log中的follower token取出
		for integral_log in integral_logs:
			if integral_log.follower_member_token:
				followers_token.append(integral_log.follower_member_token)

		# 根据token列表查出所有followers
		from business.account.member import Member
		followers = Member.from_tokens({'webapp_owner': webapp_owner, 'token': followers_token})

		# 根据followers建立token2follower的dict
		for follower in followers:
			followers_token2member[follower.token] = follower

		for integral_log in integral_logs:
			# integral = IntegralLog(webapp_owner, webapp_user, integral_log, type='integral_log')
			if integral_log.follower_member_token:
				follower = followers_token2member[integral_log.follower_member_token]
				integral = IntegralLog(webapp_owner, webapp_user, integral_log, follower=follower)
			else:
				integral = IntegralLog(webapp_owner, webapp_user, integral_log, follower=None)
			integral_logs_list.append(integral.to_dict())

		self.integral_logs = self.__get_organized_integral_log_list(integral_logs_list)

	def __get_organized_integral_log_list(self, log_list):
		"""
		获取组织后的日志列表
		"""
		# 组织后的日志列表
		organized_log_list = list()
		# 当前好友奖励
		current_friend_log_list = None
		# 当前日志日期
		current_friend_log_list_date = None

		log_dict = {}

		for log in log_list:
			current_date = log['created_at'].strftime('%Y-%m-%d')
			if log_dict.has_key(current_date):
				date_info = log_dict[current_date]
				date_info.append(log)
				log_dict[current_date] = date_info
			else:
				log_dict[current_date] = [log]

		if log_dict:
			return sorted(log_dict.items(), cmp=dateutil.cmp_datetime, key=lambda x : x[0],  reverse=False)
		else:
			return []

