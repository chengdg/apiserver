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
from core.exceptionutil import unicode_full_stack
from db.mall import models as mall_models
from db.mall import promotion_models
from db.member import models as member_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model
from business.account.member import Member
from business.mall.shopping_cart import ShoppingCart
import settings
from business.decorator import cached_context_property
from utils import regional_util
from business.account.member_order_info import MemberOrderInfo

class WebAppUser(business_model.Model):
	"""
	WebApp User
	"""
	__slots__ = (
		'id',
		'member',
		'social_account',
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
	def ship_infos(self):
		"""
		[property] 收货地址列表
		"""
		ship_infos = list(
			member_models.ShipInfo.select().where(member_models.ShipInfo.webapp_user_id == self.id,
			                                      member_models.ShipInfo.is_deleted == False))
		data = {}
		for ship_info in ship_infos:
			data_dict = ship_info.to_dict()
			data_dict['ship_id'] = ship_info.id
			data_dict.pop('created_at')
			data_dict.pop('is_deleted')
			try:
				data_dict['display_area'] = regional_util.get_str_value_by_string_ids(ship_info.area)
			except:
				data_dict['display_area'] = ''

			data[ship_info.id] = data_dict
		return data

	def select_default_ship(self, ship_id):
		"""
		选择默认收货地址
		Args:
		    ship_id:

		Returns:

		"""
		try:
			# 更新收货地址信息
			member_models.ShipInfo.update(is_selected=False).where(
				member_models.ShipInfo.webapp_user_id == self.id).execute()
			member_models.ShipInfo.update(is_selected=True).where(member_models.ShipInfo.id == ship_id).execute()
			return True
		except:
			msg = unicode_full_stack()
			watchdog_alert(msg, type='WAPI')
			return False


	def delete_ship_info(self, ship_info_id):
		"""
		删除收货地址
		Args:
		    ship_id:

		Returns:

		"""
		member_models.ShipInfo.update(is_deleted=True).where(member_models.ShipInfo.id == ship_info_id).execute()
		# 更改默认选中
		ship_infos = member_models.ShipInfo.select().where(member_models.ShipInfo.webapp_user_id == self.id,
		                                                   member_models.ShipInfo.is_deleted == False)
		selected_ships_count = ship_infos.where(member_models.ShipInfo.is_selected == True).count()
		if ship_infos.count() > 0 and selected_ships_count == 0:
			ship_info = ship_infos[0]
			ship_info.is_selected = True
			ship_info.save()
			selected_id = ship_info.id
		else:
			selected_id = 0
		return selected_id

	def modify_ship_info(self, ship_info_id, new_ship_info):
		"""
		修改收货地址
		"""
		try:
			member_models.ShipInfo.update(is_selected=False).where(member_models.ShipInfo.webapp_user_id == self.id).execute()
			member_models.ShipInfo.update(
				ship_tel=new_ship_info['ship_tel'],
				ship_address=new_ship_info['ship_address'],
				ship_name=new_ship_info['ship_name'],
				area=new_ship_info['area'],
				is_selected=True
			).dj_where(id=ship_info_id).execute()
			return True
		except:
				msg = unicode_full_stack()
				watchdog_alert(msg, type='WAPI')
				return False

	def create_ship_info(self, ship_info):
		"""
		创建收货地址
		Args:
		    ship_info:

		Returns:

		"""
		try:
			member_models.ShipInfo.update(is_selected=0).where(member_models.ShipInfo.webapp_user_id == self.id).execute()
			ship_info_id = member_models.ShipInfo.create(
				webapp_user_id=self.id,
				ship_tel=ship_info['ship_tel'],
				ship_address=ship_info['ship_address'],
				ship_name=ship_info['ship_name'],
				area=ship_info['area']
			).id
			return True, ship_info_id
		except:
				msg = unicode_full_stack()
				watchdog_alert(msg, type='WAPI')
				return False, 0

	@cached_context_property
	def shopping_cart(self):
		webapp_owner = self.context['webapp_owner']

		shopping_cart = ShoppingCart.get_for_webapp_user({
			'webapp_owner': webapp_owner,
			'webapp_user': self
		})
		return shopping_cart

	def set_purchased(self):
		"""
		设置webapp user的已购买标识
		"""
		if not self.has_purchased:
			member_models.WebAppUser.update(has_purchased=True).dj_where(id=self.id).execute()

	@cached_context_property
	def __order_info(self):
		"""
		[property] 与webapp user对应的订单信息(MemberOrderInfo)对象
		"""
		member_order_info = MemberOrderInfo.get_for_webapp_user({
			'webapp_user': self
		})

		return member_order_info

	@property
	def history_order_count(self):
		"""
		[property] webapp user总订单数
		"""
		return self.__order_info.history_order_count

	@property
	def not_payed_order_count(self):
		"""
		[property] webapp user待支付订单数
		"""
		return self.__order_info.not_payed_order_count

	@property
	def not_ship_order_count(self):
		"""
		[property] webapp user待发货订单数
		"""
		return self.__order_info.not_ship_order_count
	
	@property
	def shiped_order_count(self):
		"""
		[property] webapp user待收获订单数
		"""
		return self.__order_info.shiped_order_count

	@property
	def review_count(self):
		"""
		[property] webapp user待评论订单数
		"""
		return self.__order_info.review_count

	def to_dict(self, *extras):
		data = {}
		data['id'] = self.id
		data['member'] = self.member.to_dict()

		return data