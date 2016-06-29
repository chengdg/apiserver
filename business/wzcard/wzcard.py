# -*- coding: utf-8 -*-
import json

from eaglet.utils.resource_client import Resource
from business import model as business_model
from db.wzcard import models as wzcard_models
from db.mall import models as mall_models

from eaglet.decorator import param_required
# from db.wzcard.models import WeizoomCardRule, WeizoomCard
import logging
from decimal import Decimal
from core.decorator import deprecated
import datetime

import settings
import redis

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_COMMON_DB)


class WZCard(business_model.Model):
	__slots__ = (
		'card_number',
		'card_password',
		'source',
	)

	def __init__(self, webapp_user, webapp_owner):
		business_model.Model.__init__(self)

		self.context['webapp_user'] = webapp_user
		self.context['webapp_owner'] = webapp_owner

	# def __get_webapp_user_info(self):
	# 	"""
	# 	微众卡相关的用户信息
	# 	@return:
	# 	"""
	# 	# customer_type 使用者类型(普通会员：0、会员首单：1、非会员：2)
	# 	if self.webapp_user.member.is_subscribed:
	# 		if mall_models.Order.select().dj_where(webapp_user_id=self.webapp_user.id).count() > 0:
	# 			customer_type = 0
	# 		else:
	# 			customer_type = 1
	# 	else:
	# 		customer_type = 2
	#
	# 	return {
	# 		'customer_type': customer_type,
	# 		'customer_id': self.webapp_user.member.id,
	# 	}
	#
	# def __get_webapp_owner_info(self):
	# 	"""
	# 	微众卡相关的商户信息
	# 	@return:
	# 	"""
	# 	return {
	# 		'shop_id': self.context['webapp_owner'].id,
	# 		'shop_name': self.context['webapp_owner'].user_profile.store_name,
	# 	}
	#
	# def __get_boring_args(self):
	# 	return {
	# 		'customer_id': self.context['webapp_user'].member.id,
	# 		'exist_cards': json.dumps([]),
	# 		'valid_money': -1,  # 商品原价+运费
	# 		'customer_type': -1
	# 	}

	@staticmethod
	@param_required(['webapp_user', 'webapp_owner', 'card_number', 'card_password'])
	def check(args):
		"""
		检查微众卡，编辑订单页接口使用
		@type args: h5请求参数
		"""
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']

		if webapp_user.member.is_subscribed:
			if mall_models.Order.select().dj_where(webapp_user_id=webapp_user.id).count() > 0:
				customer_type = 0
			else:
				customer_type = 1
		else:
			customer_type = 2

		params = {
			'card_number': args['card_number'],
			'card_password': args['card_password'],

			# webapp_owner_info
			'shop_id': webapp_owner.id,
			'shop_name': webapp_owner.user_profile.store_name,

			# webapp_user_info
			'customer_id': args['webapp_user'].member.id,

			# boring_info
			'exist_cards': json.dumps([]),
			'valid_money': -1,  # 商品原价+运费
			'customer_type': customer_type
		}

		resp = Resource.use('card_apiserver').post({
			'resource': 'card.checked_card',
			'data': params
		})

		return resp

	@staticmethod
	@param_required(['card_infos'])
	def get_card_infos(args):
		"""
		检查微众卡，编辑订单页接口使用
		@type args: h5请求参数
		"""
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']

		params = {
			'card_infos': json.dumps(args['card_infos'])
		}

		resp = Resource.use('card_apiserver').post({
			'resource': 'card.get_cards',
			'data': params
		})

		return resp

	@staticmethod
	@param_required(['webapp_user', 'webapp_owner', 'card_number', 'card_password'])
	def bind(args):
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		member_id = webapp_user.member.id

		card_number = args['card_number']
		card_password = args['card_password']

		# 一人一自然天最多可输错10次密码
		today = str(datetime.datetime.today().date())

		key = 'bind_card_error_times:' + today

		error_times = r.get(key)

		if error_times >= 10:
			return False, 'wzcard:ten_times_error', None

		# 向card服务检查
		resp = WZCard.check({
			'card_number': card_number,
			'card_password': card_password,
			'webapp_user': webapp_user,
			'webapp_owner': webapp_owner
		})

		if resp:
			code = resp['code']
			data = resp['data']

			if code == 500:

				r.incr(key)
				return False, data['type'], None
			else:

				# 判断是否绑定过
				if wzcard_models.MemberHasWeizoomCard.select().dj_where(member_id=member_id,
				                                                        card_number=card_number).count() > 0:
					r.incr(key)
					return False, 'wzcard:has_bound', None

				# 判断余额是否为0
				if data['balance'] == 0:
					r.incr(key)
					return False, 'wzcard:exhausted', None


				else:
					# todo 加密
					# 绑卡
					wzcard_models.MemberHasWeizoomCard.create(
						member_id=member_id, member_name='',
						card_number=card_number, card_password=card_password,
						relation_id='',
						source=wzcard_models.WEIZOOM_CARD_SOURCE_BIND
					)

					get_card_infos_resp = WZCard.get_card_infos({
						'card_infos': [{'card_number': card_number, 'card_password': card_password}]
					})

					# 获得有效期
					if not get_card_infos_resp:
						return False, 'common:wtf', None

					card_info = get_card_infos_resp['data']['card_infos'][0]

					data['valid_time_from'] = card_info['valid_time_from']
					data['valid_time_to'] = card_info['valid_time_to']
					data['face_value'] = card_info['face_value']

					data['resource'] = wzcard_models.WEIZOOM_CARD_SOURCE_BIND
					return True, '', data


		else:
			# card微服务失败
			return False, 'common:wtf'
