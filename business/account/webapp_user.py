# -*- coding: utf-8 -*-
"""@package business.account.webapp_user
WebApp User

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
from business.account.member import Member
import settings
from business.decorator import cached_context_property


class WebAppUser(business_model.Model):
	"""
	WebApp User
	"""
	__slots__ = (
		'id',
		'member',
		'has_purchased'
	)

	@staticmethod
	@param_required(['webapp_owner', 'model'])
	def from_model(args):
		"""
		工厂方法，根据webapp user model获取WebAppUser业务对象

		@param[in] webapp_owner
		@param[in] webapp user model

		@return WebAppUser业务对象
		"""
		webapp_owner = args['webapp_owner']
		model = args['model']
		webapp_user = WebAppUser(webapp_owner, model)
		
		return webapp_user

	def __init__(self, webapp_owner, model):
		business_model.Model.__init__(self)

		if model:
			self._init_slot_from_model(model)

		self.member = Member.from_id({
			'webapp_owner': webapp_owner,
			'member_id': model.member_id
		})
		self.context['webapp_owner'] = webapp_owner

	@property
	def integral_info(self):
		"""
		[property] 积分信息
		"""
		if self.member:
			return self.member.integral_info
		else:
			integral_strategy_settings = self.context['webapp_owner'].integral_strategy_settings
			return {
				'count': 0,
				'count_per_yuan': integral_strategy_settings.integral_each_yuan,
				'usable_integral_percentage_in_order' : 1000,
				'usable_integral_or_conpon' : integral_strategy_settings.usable_integral_or_conpon
			}

	@property
	def ship_info(self):
		"""
		[property] 收货地址
		"""
		ship_infos = list(member_models.ShipInfo.select().dj_where(webapp_user_id=self.id, is_deleted=False, is_selected=True))
		if len(ship_infos) > 0:
			ship_info = ship_infos[0]
			return {
				"id": ship_info.id,
				"name": ship_info.ship_name,
				"tel": ship_info.ship_tel,
				"address": ship_info.ship_address,
				"area": ship_info.area,
			}
			return ship_infos[0]
		else:
			return None

	@property
	def ship_infos(self):
		"""
		[property] 收货地址集合
		"""
		try:
			return list(member_models.ShipInfo.select().dj_where(webapp_user_id=self.id, is_deleted=False))
		except:
			return None

	def set_purchased(self):
		"""
		设置webapp user的已购买标识
		"""
		if not self.has_purchased:
			member_models.WebAppUser.update(has_purchased=True).dj_where(id=self.id).execute()


	# def to_dict(self, *extras):
	# 	properties = ['ship_infos', 'ship_info', 'integral_info', 'is_binded']
	# 	if extras:
	# 		properties.extend(extras)
	# 	return business_model.Model.to_dict(self, *properties)