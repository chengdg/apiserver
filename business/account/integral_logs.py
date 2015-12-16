# -*- coding: utf-8 -*-
"""@package business.account.integral_logs
积分日子集合

"""

import json
from bs4 import BeautifulSoup
import math
import itertools

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from db.member import models as member_models
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.order_product import OrderProduct 
from business.mall.forbidden_coupon_product_ids import ForbiddenCouponProductIds
from business.account.integral_log import IntegralLog 
from utils import dateutil


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
		integral_logs = member_models.MemberIntegralLog.select().dj_where(member_id=webapp_user.member.id).order_by('-created_at')

		for integral_log in integral_logs:
			integral_logs_list.append(IntegralLog.from_model({
					'webapp_user': webapp_user,
					'webapp_owner': webapp_owner,
					'model': integral_log
				}).to_dict())
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

