# -*- coding: utf-8 -*-
"""@package business.account.webapp_owner
WebApp Owner

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
from db.wzcard import models as wzcard_models
from db.account import models as account_models
#import resource
from core.watchdog.utils import watchdog_alert
from business.decorator import cached_context_property
from business import model as business_model
from business.mall.mall_data import MallData
from business.account.webapp_owner_info import WebAppOwnerInfo
import settings
from core.decorator import deprecated
import logging


class WebAppOwner(business_model.Model):
	__slots__ = (
		'id',
		'webapp_id'
	)

	@staticmethod
	@param_required(['woid'])
	def get(args):
		"""
		工厂方法，根据webapp owner id获取WebAppOwner业务对象

		@param[in] woid

		@return WebAppOwner业务对象
		"""
		webapp_owner_id = args['woid']

		webapp_owner = WebAppOwner(webapp_owner_id)
		return webapp_owner

	def __init__(self, webapp_owner_id):
		business_model.Model.__init__(self)
		webapp_owner_profile = account_models.UserProfile.get(user=webapp_owner_id)
		self.webapp_id = webapp_owner_profile.webapp_id
		self.id = webapp_owner_profile.user_id

	@cached_context_property
	def __mall_data(self):
		"""
		[property] 与webapp owner id关联的MallData业务对象
		"""
		return MallData.get({
			'woid': self.id
		})

	@cached_context_property
	#@property
	def __webapp_owner_info(self):
		"""
		[property] 与webapp owner id关联的WebAppOwerInfo业务对象
		"""
		return WebAppOwnerInfo.get({
			'woid': self.id
		})

	@property
	def mall_config(self):
		"""
		[property] 商城配置
		"""
		return self.__mall_data.mall_config

	@property
	def postage_configs(self):
		"""
		[property] 运费配置
		"""
		return self.__mall_data.postage_configs

	@property
	def system_postage_config(self):
		"""
		[property] 当前正在使用的运费配置
		"""
		return filter(lambda config: config['is_used'], self.postage_configs)[0]

	@property
	def product_model_properties(self):
		"""
		[property] 商品规格属性
		"""
		return self.__mall_data['product_model_properties']

	@property
	def red_envelope(self):
		"""
		[property] 红包
		"""
		return self.__webapp_owner_info.red_envelope

	@property
	def global_navbar(self):
		"""
		[property] 全局导航配置
		"""
		return self.__webapp_owner_info.global_navbar

	@property
	def integral_strategy_settings(self):
		"""
		[property] 积分使用策略配置
		"""
		return self.__webapp_owner_info.integral_strategy_settings

	@property
	def pay_interfaces(self):
		"""
		[property] 支付方式配置
		"""
		if self.has_wzcard_permission:
			return self.__webapp_owner_info.pay_interfaces
		else:
			return filter(lambda x: x['type'] != mall_models.PAY_INTERFACE_WEIZOOM_COIN, self.__webapp_owner_info.pay_interfaces)

	@property
	@deprecated
	def is_weizoom_card_permission(self):
		"""
		[property] 是否开启了微众卡权限

		@note 改用`has_wzcard_permission`
		"""
		return self.__webapp_owner_info.is_weizoom_card_permission

	@property
	def has_wzcard_permission(self):
		"""
		[property] 是否开启了微众卡权限
		"""
		return self.__webapp_owner_info.is_weizoom_card_permission


	def __set_wzcard_permission(self, is_enabled):
		"""
		设置微众卡的权限

		@param is_enabled True表示开启；False表示禁止
		"""
		# 修改数据库
		permissions = wzcard_models.AccountHasWeizoomCardPermissions.select().dj_where(owner_id=self.id)
		if permissions.count()>0:
			permission = permissions[0]
			permission.is_can_use_weizoom_card = is_enabled
			permission.save()
		else:
			permission = wzcard_models.AccountHasWeizoomCardPermissions.create(
				owner_id=self.id,
				is_can_use_weizoom_card=is_enabled)
		
		# 让webapp_onwer_info清除缓存
		(self.__webapp_owner_info).purge_cache()

		return permission

	def enable_wzcard_permission(self):
		"""
		开启微众卡权限

		@retval void
		"""
		self.__set_wzcard_permission(True)


	def disable_wzcard_permission(self):
		"""
		关闭微众卡权限

		@retval void
		"""
		self.__set_wzcard_permission(False)


	@property
	def qrcode_img(self):
		"""
		[property] 二维码图片
		"""
		return self.__webapp_owner_info.qrcode_img

	@property
	def member_grades(self):
		"""
		[property] 会员等级
		"""
		return self.__webapp_owner_info.member_grades

	@property
	def member2grade(self):
		"""
		[property] <member_grade_id, member_grade>映射集合
		"""
		return self.__webapp_owner_info.member2grade

	@property
	def default_member_tag(self):
		"""
		[property] 默认会员等级
		"""
		return self.__webapp_owner_info.default_member_tag

	@property
	def weixin_mp_user_access_token(self):
		"""
		[property] 默认会员等级
		"""
		return self.__webapp_owner_info.weixin_mp_user_access_token



