# -*- coding: utf-8 -*-
import json

from eaglet.core import watchdog
from eaglet.utils.resource_client import Resource
from business import model as business_model
from db.wzcard import models as wzcard_models
from db.mall import models as mall_models

from eaglet.decorator import param_required

import datetime

import settings
import redis

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_COMMON_DB)


class WZCard(business_model.Model):
	__slots__ = (
		'card_number',
		'card_password',
		'source',

		'valid_time_from',
		'valid_time_to',
		'face_value',
		'balance',  # 'used', 'unused','empty', 'inactive', 'expired'
		'bound_at',
		'status'

	)

	def __init__(self, member_has_card_model, card_detail):
		business_model.Model.__init__(self)

		self.card_number = card_detail['card_number']
		self.card_password = card_detail['card_password']
		self.face_value = card_detail['face_value']
		self.valid_time_from = card_detail['valid_time_from']
		self.valid_time_to = card_detail['valid_time_to']
		self.balance = "%.2f" % float(card_detail['balance'])
		# self.status_text = card_detail['status_text']
		self.status = card_detail.get('internal_status', '11')

		if member_has_card_model:
			self.source = member_has_card_model.source
			self.bound_at = member_has_card_model.id

		# self.context['webapp_user'] = webapp_user
		# self.context['webapp_owner'] = webapp_owner

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

		times_key = 'bind_card_error_times_{}:{}'.format(today, str(webapp_user.id))

		times_value = r.get(times_key)

		error_times = int(times_value) if times_value else 0

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

				r.incr(times_key)
				return False, data['type'], None
			else:

				# 判断是否绑定过
				if wzcard_models.MemberHasWeizoomCard.select().dj_where(member_id=member_id,
				                                                        card_number=card_number).count() > 0:
					r.incr(times_key)
					return False, 'wzcard:has_bound', None

				# 判断余额是否为0
				if float(data['balance']) == 0:
					r.incr(times_key)
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

					card_info = get_card_infos_resp['data']['card_infos'][0].values()[0]

					data['valid_time_from'] = card_info['valid_time_from']
					data['valid_time_to'] = card_info['valid_time_to']
					data['face_value'] = card_info['face_value']

					data['resource'] = wzcard_models.WEIZOOM_CARD_SOURCE_BIND
					return True, '', data


		else:
			# card微服务失败
			return False, 'common:wtf'

	@staticmethod
	@param_required(['member_has_cards'])
	def from_member_has_cards(args):
		"""
		member_has_cards:MemberHasWeizoomCard models

		"""
		member_has_cards = list(args['member_has_cards'])

		if len(member_has_cards) == 0:
			return True, [], []

		card_number2models = {a.card_number: a for a in member_has_cards}
		card_numbers_passwords = [{'card_number': a.card_number, 'card_password': a.card_password} for a in
		                          member_has_cards]

		resp = WZCard.get_card_infos({
			'card_infos': card_numbers_passwords
		})

		if resp:

			card_infos = resp['data']['card_infos']
			cards = []
			for card in card_infos:
				card_detail = card.values()[0]

				card_number = card.keys()[0]
				member_has_card_model = card_number2models[card_number]

				cards.append(WZCard(member_has_card_model, card_detail))

			cards = sorted(cards, key=lambda x: -x.bound_at)

			usable_cards = []
			unusable_cards = []
			_cards = []
			for card in cards:
				if card.status in ('used', 'unused'):
					usable_cards.append(card)
				elif card.status in ('empty', 'expired'):
					_cards.append(card)
				elif card.status == 'inactive':
					unusable_cards.append(card)
				else:
					watchdog.alert({
						'description': u'Error card status',
						'card_number': card.card_number,
						'card_status': card.status
					})
			unusable_cards.extend(_cards)

			return True, usable_cards, unusable_cards


		else:
			return False, None, None
