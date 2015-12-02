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
import logging

class Member(business_model.Model):
	"""
	会员
	"""
	__slots__ = (
		'id',
		'grade_id',
		'username_hexstr',
		'webapp_user',
		'is_subscribed',
		'created',
		'token',
		'webapp_id'
	)

	@staticmethod
	def from_models(query):
		pass

	@staticmethod
	@param_required(['webapp_owner', 'model'])
	def from_model(args):
		"""
		工厂对象，根据member model获取Member业务对象

		@param[in] webapp_owner
		@param[in] model: member model

		@return Member业务对象
		"""
		webapp_owner = args['webapp_owner']
		model = args['model']

		member = Member(webapp_owner, model)
		member._init_slot_from_model(model)
		return member

	@staticmethod
	@param_required(['webapp_owner', 'member_id'])
	def from_id(args):
		"""
		工厂对象，根据member id获取Member业务对象

		@param[in] webapp_owner
		@param[in] member_id: 会员的id

		@return Member业务对象
		"""
		webapp_owner = args['webapp_owner']
		member_id = args['member_id']
		try:
			member_db_model = member_models.Member.get(id=member_id)
			return Member.from_model({
				'webapp_owner': webapp_owner,
				'model': member_db_model
			})
		except:
			return None

	@staticmethod
	@param_required(['webapp_owner', 'token'])
	def from_token(args):
		"""
		工厂对象，根据member id获取Member业务对象

		@param[in] webapp_owner
		@param[in] token: 会员的token

		@return Member业务对象
		"""
		webapp_owner = args['webapp_owner']
		token = args['token']
		try:
			member_db_model = member_models.Member.get(webapp_id=webapp_owner.webapp_id,token=token)
			return Member.from_model({
				'webapp_owner': webapp_owner,
				'model': member_db_model
			})
		except:
			return None	

	def __init__(self, webapp_owner, model):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['db_model'] = model

	@cached_context_property
	def __grade(self):
		"""
		[property] 会员等级信息
		"""
		member_model = self.context['db_model']
		webapp_owner = self.context['webapp_owner']

		if not member_model:
			return None

		member_grade_id = member_model.grade_id
		member_grade = webapp_owner.member2grade.get(member_grade_id, '')
		return member_grade

	@property
	def discount(self):
		"""
		[property] 会员折扣

		@return 返回二元组(grade_id, 折扣百分数)
		"""
		member_model = self.context['db_model']
		if not member_model:
			return -1, 100

		member_grade = self.__grade
		if member_grade:
			return member_model.grade_id, member_grade.shop_discount
		else:
			return member_model.grade_id, 100

	@property
	def grade(self):
		"""
		[property] 会员等级
		"""
		return self.__grade

	@cached_context_property
	def __info(self):
		"""
		[property] 与会员对应的MemberInfo model对象
		"""
		member_model = self.context['db_model']
		if not member_model:
			return None

		try:
			member_info = member_models.MemberInfo.get(member=member_model.id)
		except:
			member_info = member_models.MemberInfo()
			member_info.member_id = member_model.id
			member_info.name = ''
			member_info.weibo_name = ''
			member_info.phone_number = None
			member_info.sex = member_models.SEX_TYPE_UNKOWN
			member_info.is_binded = False

		if member_info.phone_number and len(member_info.phone_number) > 10:
			member_info.phone =  '%s****%s' % (member_info.phone_number[:3], member_info.phone_number[-4:])

		return member_info

	@property
	def phone(self):
		"""
		[property] 会员绑定的手机号码
		"""

		return self.__info.phone

	@property
	def name(self):
		"""
		[property] 会员名
		"""

		return self.__info.name

	@property
	def is_binded(self):
		"""
		[property] 会员是否进行了绑定
		"""
		return self.__info.is_binded

	@cached_context_property
	def user_icon(self):
		"""
		[property] 会员头像
		"""
		#TODO2: 实现获取会员头像
		logging.info(u'TODO2: 实现获取会员头像')
		return ''

	@cached_context_property
	def integral_info(self):
		"""
		[property] 会员积分信息
		"""
		member_model = self.context['db_model']
		if member_model:
			count = member_model.integral
			grade = self.__grade
			if grade:
				usable_integral_percentage_in_order = grade.usable_integral_percentage_in_order
			else:
				usable_integral_percentage_in_order = 100
		else:
			count = 0
			usable_integral_percentage_in_order = 100

		integral_strategy_settings = self.context['webapp_owner'].integral_strategy_settings
		return {
			'count': count,
			'count_per_yuan': integral_strategy_settings.integral_each_yuan,
			'usable_integral_percentage_in_order' : usable_integral_percentage_in_order,
			'usable_integral_or_conpon' : integral_strategy_settings.usable_integral_or_conpon
		}

	@property
	def integral(self):
		"""
		[property] 会员积分数值
		"""
		member_model = self.context['db_model']

		return member_model.integral

	@cached_context_property
	def username_for_html(self):
		"""
		[property] 兼容html显示的会员名
		"""
		if (self.username_hexstr is not None) and (len(self.username_hexstr) > 0):
			username = emojicons_util.encode_emojicons_for_html(self.username_hexstr, is_hex_str=True)
		else:
			username = emojicons_util.encode_emojicons_for_html(self.username)		

		try:
			username.decode('utf-8')
		except:
			username = self.username_hexstr

		return username

	@cached_context_property
	def __order_info(self):
		"""
		[property] 与会员对应的订单信息(MemberOrderInfo)对象
		"""
		member_order_info = MemberOrderInfo.get_for_webapp_user({
			'webapp_user': self.webapp_user
		})

		return member_order_info

	@property
	def history_order_count(self):
		"""
		[property] 会员总订单数
		"""
		return self.__order_info.history_order_count

	@property
	def not_payed_order_count(self):
		"""
		[property] 会员待支付订单数
		"""
		return self.__order_info.not_payed_order_count

	@property
	def not_ship_order_count(self):
		"""
		[property] 会员待发货订单数
		"""
		return self.__order_info.not_ship_order_count
	
	@property
	def shiped_order_count(self):
		"""
		[property] 会员待收获订单数
		"""
		return self.__order_info.shiped_order_count

	@property
	def review_count(self):
		"""
		[property] 会员待评论订单数
		"""
		return self.__order_info.review_count

	@cached_context_property
	def wishlist_product_count(self):
		"""
		[property] 会员收藏商品的数量
		"""
		webapp_owner = self.context['webapp_owner']
		return mall_models.MemberProductWishlist.select().dj_where(
			owner_id = webapp_owner.id,
			member_id = self.id,
			is_collect=True
		).count()

	def is_collect_product(self, product_id):
		"""是否收藏了product_id对应的商品
		"""
		webapp_owner = self.context['webapp_owner']
		return mall_models.MemberProductWishlist.select().dj_where(
			owner_id = webapp_owner.id,
			member_id = self.id,
			product_id = product_id,
			is_collect=True
		).count() > 0

	@cached_context_property
	def market_tools(self):
		"""
		[property] 会员参与的营销工具集合
		"""
		#TODO2: 实现营销工具集合
		print u'TODO2: 实现营销工具集合'
		return []

	@staticmethod
	def empty_member():
		"""工厂方法，创建空的member对象

		@return Member对象
		"""
		member = Member(None, None)
		return member

	# def to_dict(self, *extras):
	# 	properties = ['username_for_html', 'integral', 'user_icon', 'is_binded']
	# 	if extras:
	# 		properties.extend(extras)
	# 	return business_model.Model.to_dict(self, *properties)

	# @property
	# def token(self):
	# 	"""
	# 	[property] 会员购物车中的商品数量
	# 	"""
	# 	return self.token

