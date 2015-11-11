# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
from wapi.mall import promotion_models
from wapi.user import models as account_models
import resource
from core.watchdog.utils import watchdog_alert
from business.decorator import cached_context_property
from business import model as business_model
from business.mall.mall_data import MallData
import settings


class WebAppOwner(business_model.Model):
	__slots__ = (
		'id',
		'webapp_id'
	)

	@staticmethod
	@param_required(['woid'])
	def get(args):
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
		return MallData.get({
			'woid': self.id
		})

	@cached_context_property
	def __webapp_owner_info(self):
		return MallData.get({
			'woid': self.id
		})

	@property
	def mall_config(self):
		"""
		[property] 商城配置
		"""
		return self.__mall_data['mall_config']

	@property
	def postage_configs(self):
		"""
		[property] 运费配置
		"""
		return self.__mall_data['postage_configs']

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
		return self.__webapp_owner_info['red_envelope']

	@property
	def global_navbar(self):
		"""
		[property] 全局导航配置
		"""
		return self.__webapp_owner_info['global_navbar']

	@property
	def integral_strategy_settings(self):
		"""
		[property] 积分使用策略配置
		"""
		return self.__webapp_owner_info['integral_strategy_settings']

	@property
	def pay_interfaces(self):
		"""
		[property] 支付方式配置
		"""
		return self.__webapp_owner_info['pay_interfaces']

	@property
	def is_weizoom_card_permission(self):
		"""
		[property] 是否开启了微众卡权限
		"""
		return self.__webapp_owner_info['is_weizoom_card_permission']

	@property
	def qrcode_img(self):
		"""
		[property] 二维码图片
		"""
		return self.__webapp_owner_info['qrcode_img']
