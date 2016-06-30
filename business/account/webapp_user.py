# -*- coding: utf-8 -*-
"""@package business.account.webapp_user
WebApp User

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util

from core.exceptionutil import unicode_full_stack
from db.mall import models as mall_models
from db.mall import promotion_models
from db.member import models as member_models
#import resource
from eaglet.core import watchdog
from business import model as business_model
from business.account.member import Member
from business.mall.shopping_cart import ShoppingCart
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from util import regional_util
from business.account.member_order_info import MemberOrderInfo
from business.account.social_account import SocialAccount
from business.wzcard.wzcard_package import WZCardPackage

from business.mall.coupon.coupon import Coupon


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
	@param_required(['webapp_owner', 'member_id'])
	def from_member_id(args):
		"""
		工厂方法，根据webapp user model获取WebAppUser业务对象

		@param[in] webapp_owner
		@param[in] member_id member_id

		@return WebAppUser业务对象
		"""
		webapp_owner = args['webapp_owner']
		member_id = args['member_id']
		#try:
		model = member_models.WebAppUser.select().dj_where(webapp_id=webapp_owner.webapp_id, member_id=member_id).first()
		webapp_user = WebAppUser(webapp_owner, model)
		return webapp_user
		# except:
		# 	return None

	@staticmethod
	@param_required(['webapp_owner', 'id'])
	def from_id(args):
		"""
		工厂方法，根据webapp user model获取WebAppUser业务对象

		@param[in] webapp_owner
		@param[in] id

		@return WebAppUser业务对象
		"""
		webapp_owner = args['webapp_owner']
		id = args['id']
		#try:
		model = member_models.WebAppUser.get(id=id)
		webapp_user = WebAppUser(webapp_owner, model)
		return webapp_user
		

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

	def is_match_member_grade(self, member_grade_id):
		"""
		判断webapp_user是否符合指定的会员等级

		Parameters
			[in] member_grade_id: 会员等级

		Returns
			True: 符合指定的会员等级
			False: 不符合指定的会员等级
		"""
		if not self.member:
			#不是会员
			return False

		if self.member.grade_id == member_grade_id:
			return True
		else:
			return False

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
	def selected_ship_info(self):
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
			watchdog.alert(msg, type='WAPI')
			return False


	def delete_ship_info(self, ship_info_id):
		"""
		删除收货地址
		@param ship_info_id
		@return selected_id

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
		@param ship_info_id: 收货地址id
		@param new_ship_info: 新信息
		@return bool
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
				watchdog.alert(msg, type='WAPI')
				return False

	def create_ship_info(self, ship_info):
		"""
		@param ship_info: 收货地址信息，字典类型
		@return ship_info_id
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
				watchdog.alert(msg, type='WAPI')
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

	@property
	def finished_order_count(self):
		"""
		[property] webapp user已完成状态订单单数
		"""
		return self.__order_info.finished_count

	def to_dict(self, *extras):
		data = {}
		data['id'] = self.id
		data['member'] = self.member.to_dict()

		return data

	def collected_product(self, product_id):
		"""收藏了product_id对应的商品
		"""
		webapp_owner = self.context['webapp_owner']
		if mall_models.MemberProductWishlist.select().dj_where(
				owner_id = webapp_owner.id,
				member_id = self.member.id,
				product_id = product_id,
			).count() > 0:

			mall_models.MemberProductWishlist.update(is_collect=True).dj_where(
				owner_id = webapp_owner.id,
				member_id = self.member.id,
				product_id = product_id,
			).execute()
		else:
			
			mall_models.MemberProductWishlist.create(
				owner = webapp_owner.id,
				member_id = self.member.id,
				product_id = product_id,
				is_collect=True
			)

	def cancel_collected_product(self, product_id):
		"""取消收藏了product_id对应的商品
		"""
		webapp_owner = self.context['webapp_owner']
		mall_models.MemberProductWishlist.update(is_collect=False).dj_where(
			owner_id = webapp_owner.id,
			member_id = self.member.id,
			product_id = product_id,
			).execute()
		
	@cached_context_property
	def collected_products(self):
		"""
		[property] 会员收藏商品的集合
		"""
		webapp_owner = self.context['webapp_owner']
		
		ids = [memner_product_wish.product_id for memner_product_wish in mall_models.MemberProductWishlist.select().dj_where(
			owner_id = webapp_owner.id,
			member_id = self.member.id,
			is_collect=True
			).order_by(-mall_models.MemberProductWishlist.add_time)] 

		products = Product.from_ids({
			'webapp_owner': webapp_owner,
			'member': self.member,
			'product_ids': ids
		})
		products_dict_list = []
		for id in ids:
			for product in products:
				if product.id == id:
					products_dict_list.append(product.to_dict())
					break

		return products_dict_list

	@cached_context_property
	def collected_product_count(self):
		"""
		[property] 会员收藏商品的数量
		"""
		webapp_owner = self.context['webapp_owner']
		return mall_models.MemberProductWishlist.select().dj_where(
			owner_id = webapp_owner.id,
			member_id = self.member.id,
			is_collect=True
		).count()

	def is_collect_product(self, product_id):
		"""是否收藏了product_id对应的商品
		"""
		webapp_owner = self.context['webapp_owner']
		return mall_models.MemberProductWishlist.select().dj_where(
			owner_id = webapp_owner.id,
			member_id = self.member.id,
			product_id = product_id,
			is_collect=True
		).count() > 0

	@property
	def discount(self):
		return self.member.discount

	@property
	def grade(self):
		"""
		[property] 会员等级
		"""
		return self.member.grade

	@property
	def phone(self):
		"""
		[property] 会员绑定的手机号码加密
		"""
		return self.member.phone

	@property
	def phone_number(self):
		"""
		[property] 会员绑定的手机号码
		"""
		return self.member.phone_number

	@property
	def name(self):
		"""
		[property] 会员名
		"""
		return self.member.name

	@cached_context_property
	def user_icon(self):
		"""
		[property] 会员头像
		"""
		return self.member.user_icon

	@cached_context_property
	def integral_info(self):
		"""
		[property] 会员积分信息
		"""
		return self.member.integral_info

	@property
	def integral(self):
		"""
		[property] 会员积分数值
		"""
		return self.member.integral

	@cached_context_property
	def username_for_html(self):
		"""
		[property] 兼容html显示的会员名
		"""
		return self.member.username_for_html

	def cleanup_cache(self):
		"""
		[property] 清除缓存
		"""
		key = 'member_{webapp:%s}_{openid:%s}' % (self.member.webapp_id, self.openid)
		cache_util.delete_cache(key)

	def cleanup_order_info_cache(self):
		key = "webapp_order_stats_{wu:%d}" % (self.id)
		cache_util.delete_cache(key)

		# 清除后台订单计数角标缓存
		from core.cache.utils import r
		key_for_weapp_order_list = 'webapp_unread_order_count_{wa:%s}' % self.member.webapp_id
		# cache_util.delete_cache(key_for_weapp_order_list)
		r.delete(':1:' + key_for_weapp_order_list)

	@cached_context_property
	def openid(self):
		"""
		[property] 兼容html显示的会员名
		"""
		social_account = SocialAccount.from_member_id({
			'webapp_owner': self.context['webapp_owner'],
			'member_id': self.member.id
			})
		return social_account.openid

	def use_integral(self, integral_count):
		if integral_count == 0:
			return True, None
		from business.account.integral import Integral
		return Integral.use_integral_to_buy({
			'webapp_user': self,
			'integral_count': -integral_count
			})

	def integral_roll_back(self, integral_count, log_id):
		pass

	def can_use_integral(self, integral):
		"""
		检查是否可用数量为integral的积分
		"""
		if not self.member:
			return False

		remianed_integral = member_models.Member.get(id=self.member.id).integral
		if remianed_integral >= integral:
			return True
		else:
			return False

	@cached_context_property
	def is_binded(self):
		return self.member.is_binded

	@cached_context_property
	def coupons(self):
		return Coupon.get_coupons_by_webapp_user({
			'webapp_user': self
		})

	@cached_context_property
	def all_coupons(self):
		return Coupon.get_all_coupons_by_webapp_user({
			'webapp_user': self
		})

	#绑定相关
	@staticmethod
	def can_binding_phone(webapp_id, phone_number):
		# return member_models.MemberInfo.select().dj_where(member__webapp_id=webapp_id, phone_number=phone_number, is_binded=True).count() == 0
		return member_models.MemberInfo.select().join(member_models.Member).where(member_models.Member.webapp_id==webapp_id, member_models.MemberInfo.phone_number==phone_number, member_models.MemberInfo.is_binded==True).count() == 0

	def update_phone_captcha(self, phone_number, captcha, sessionid):
		if phone_number and captcha:
			member_models.MemberInfo.update(session_id=sessionid, phone_number=phone_number, captcha=captcha, binding_time=datetime.now()).dj_where(member_id=self.member.id).execute()

	@cached_context_property
	def captcha(self):
		"""
		[property] 手机验证码
		"""
		return self.member.captcha

	@cached_context_property
	def captcha_session_id(self):
		"""
		[property] 手机验证码
		"""
		return self.member.captcha_session_id

	@cached_context_property
	def binded(self):
		member_models.MemberInfo.update(binding_time=datetime.now(), is_binded=True).dj_where(member_id=self.member.id).execute()
	
	def set_force_purchase(self):
		"""
		设置强制购买模式

		强制购买模式可以避开一些资源检查，比如：买赠活动的赠品库存不足
		"""
		self.context['is_force_purchase'] = True

	def is_force_purchase(self):
		"""
		获取当前是否是强制购买模式
		"""
		return self.context.get('is_force_purchase', False)

	def update_pay_info(self, money, order_payment_time):
		"""
		@warning 此处修改的member只修改了db_model的数据。
		@param money:
		@param order_payment_time:
		@return:
		"""
		self.set_purchased()
		pay_money = None
		if money > 0:
			member = member_models.Member.get(id=self.member.id)
			member.pay_money = member.pay_money + money
			member.pay_times = member.pay_times + 1
			member.last_pay_time = order_payment_time
			# member.purchase_frequency += 1
			try:
				member.unit_price = member.pay_money/member.pay_times
			except:
				member.unit_price = 0
			member.save()
			pay_money = member.pay_money
		self.update_member_grade(pay_money)
		self.cleanup_cache()

	def update_member_grade(self, pay_money=None):
		if not pay_money:
			pay_money = self.member.pay_money

		finished_order_count = self.finished_order_count
		webapp_owner = self.context['webapp_owner']
		grades = sorted(filter(lambda x: x.is_auto_upgrade and x.id > self.grade.id, webapp_owner.member_grades))
		is_all_conditions = webapp_owner.integral_strategy_settings.is_all_conditions

		new_grade = None
		for grade in grades:
			if is_all_conditions:
				if pay_money >= grade.pay_money and finished_order_count >= grade.pay_times:
					new_grade = grade
			else:
				if pay_money >= grade.pay_money or finished_order_count >= grade.pay_times:
					new_grade = grade

			if new_grade:
				member = member_models.Member.get(id=self.member.id)
				member.grade = new_grade
				member.save()
				break


	@cached_context_property
	def wzcard_package(self):

		return WZCardPackage.from_webapp_user({'webapp_user': self})
