# -*- coding: utf-8 -*-
"""@package business.account.integral

"""

import json
from bs4 import BeautifulSoup
import math
import itertools
import uuid
import time
import random
import string

from eaglet.decorator import param_required
from db.member import models as member_models
from db.mall import models as mall_models

from business import model as business_model
import settings
from business.decorator import cached_context_property
from eaglet.core import watchdog
from core.exceptionutil import unicode_full_stack

from business.account.webapp_user import WebAppUser

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
		'review_increase',
		'order_money_percentage_for_each_buy',
		'buy_via_offline_increase_count_percentage_for_author',
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
		#TODO-bert 调整统一参数
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
		member = member_models.Member.get(id=member.id)
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
				webapp_user.cleanup_cache()

			return True, integral_log.id
		except:
			notify_message = u"update_member_integral member_id:{}, cause:\n{}".format(member.id, unicode_full_stack())
			watchdog.error(notify_message)
			return False, None


	@staticmethod
	def use_integral_to_buy(args):
		webapp_user = args['webapp_user']
		use_count = int(args['integral_count'])

		if use_count == 0:
			return True, None

		return Integral.increase_member_integral({
			'integral_increase_count': use_count,
			'webapp_user': webapp_user,
			'member':webapp_user.member,
			'event_type':  member_models.USE
			})

	@staticmethod
	def roll_back_integral(args):
		webapp_user = args['webapp_user']
		integral_log_id = args['integral_log_id']
		integral_count = args['integral_count']
		#TODO-bert 增加watchdog
		member_models.Member.update(integral=member_models.Member.integral + integral_count).dj_where(id=webapp_user.member.id).execute()
		member_models.MemberIntegralLog.delete().dj_where(id=integral_log_id).execute()

	@staticmethod
	def return_integral(args):
		"""
		返还积分

		与roll_back_integral()区别：return_integral()不删除integral_log。
		"""
		webapp_user = args['webapp_user']
		return_count = args['return_count']

		if return_count <= 0:
			return

		return Integral.increase_member_integral({
			'integral_increase_count': return_count,
			'webapp_user': webapp_user,
			'member':webapp_user.member,
			'event_type':  member_models.RETURN_BY_SYSTEM
			})

	@staticmethod
	def increase_after_order_payed_finsh(args):
		#print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.1'
		order_id = args['order_id']
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		#print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.2',order_id
		integral_strategy = webapp_owner.integral_strategy_settings
		order = mall_models.Order.get(id=order_id)
		#print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.3'
		try:
			mall_order_from_shared = mall_models.MallOrderFromSharedRecord.select().dj_where(order_id=order_id).first()
			if mall_order_from_shared:
				fmt = mall_order_from_shared.fmt
			else:
				fmt = None
		except:
			fmt = None
		#print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.4 fmt:',fmt
		member = webapp_user.member

		if member and order:
			#print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.5 fmt:',fmt
			if member.token != fmt:
				try:
					followed_member = member_models.Member.get(token=fmt)
					if followed_member.webapp_id != member.webapp_id:
						followed_member = None
				except:
					followed_member = None
			else:
				followed_member = None

			if not integral_strategy:
				integral_strategy_settings = member_models.IntegralStrategySttings.get(webapp_id=webapp_owner.webapp_id)
			#print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.46fmt:',integral_strategy
			if integral_strategy:
				#print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.7:'
				increase_count = integral_strategy.buy_via_shared_url_increase_count_for_author
				#给好友奖励（分享链接购买）

				if increase_count > 0 and followed_member:

					followed_webapp_user = WebAppUser.from_member_id({
						'webapp_owner': webapp_owner,
						'member_id': followed_member.id
						})

					Integral.increase_member_integral({
						'integral_increase_count': increase_count,
						'webapp_user': followed_webapp_user,
						'member': followed_member,
						'event_type':  member_models.FOLLOWER_BUYED_VIA_SHARED_URL
						})

					#self.increase_member_integral(followed_member, \
					#		increase_count, FOLLOWER_BUYED_VIA_SHARED_URL, None)
				#购物返利
				#print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.8:'
				if  integral_strategy.buy_award_count_for_buyer > 0:
					#print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.81:',integral_strategy.buy_award_count_for_buyer
					Integral.increase_member_integral({
						'integral_increase_count': integral_strategy.buy_award_count_for_buyer,
						'webapp_user': webapp_user,
						'member': member,
						'event_type':  member_models.BUY_AWARD
						})

					#self.increase_member_integral(member, \
					#	integral_strategy.buy_award_count_for_buyer, BUY_AWARD)

				#购物返利 按订单比例增加
				if order and order.final_price > 0:
					#print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.9:'
					order_money_percentage_for_each_buy = float(integral_strategy.order_money_percentage_for_each_buy)
					increase_count_integral = int(order_money_percentage_for_each_buy * float(order.final_price))
					if increase_count_integral > 0:
						#self.increase_member_integral(member, increase_count_integral, BUY_AWARD)
						Integral.increase_member_integral({
							'integral_increase_count': increase_count_integral,
							'webapp_user': webapp_user,
							'member': member,
							'event_type':  member_models.BUY_AWARD
							})
				#print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.10:'

				if member and member.is_subscribed:
					member_relation = member_models.MemberFollowRelation.select().dj_where(follower_member_id=member.id, is_fans=True).first()
					if member_relation:
						try:
							father_member = member_models.Member.get(id=member_relation.member_id)
						except:
							father_member = None
					else:
						father_member = None

					if father_member:
						father_webapp_user = WebAppUser.from_member_id({
							'webapp_owner': webapp_owner,
							'member_id': father_member.id
							})
						if integral_strategy.buy_via_offline_increase_count_for_author > 0:
							#self.increase_member_integral(father_member, integral_strategy.buy_via_offline_increase_count_for_author, BUY_INCREST_COUNT_FOR_FATHER)

							Integral.increase_member_integral({
								'integral_increase_count': integral_strategy.buy_via_offline_increase_count_for_author,
								'webapp_user': father_webapp_user,
								'member': father_member,
								'event_type':  member_models.BUY_INCREST_COUNT_FOR_FATHER
								})


						if order.final_price > 0 and integral_strategy.buy_via_offline_increase_count_percentage_for_author:
							try:
								buy_via_offline_increase_count_percentage_for_author = float(integral_strategy.buy_via_offline_increase_count_percentage_for_author)
								integral_count = int(order.final_price * buy_via_offline_increase_count_percentage_for_author)
								#self.increase_member_integral(father_member, integral_count, BUY_INCREST_COUNT_FOR_FATHER)
								Integral.increase_member_integral({
									'integral_increase_count': integral_count,
									'webapp_user': father_webapp_user,
									'member': father_member,
									'event_type':  member_models.BUY_INCREST_COUNT_FOR_FATHER
									})
							except:
								notify_message = u"increase_father_member_integral_by_child_member_buyed cause:\n{}".format(unicode_full_stack())
								watchdog.error(notify_message)