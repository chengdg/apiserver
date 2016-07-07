# -*- coding: utf-8 -*-
import json

from eaglet.core import watchdog
from eaglet.core.cache import utils as cache_util
from eaglet.decorator import param_required
from eaglet.utils.resource_client import Resource

from business import model as business_model
from db.mall import models as mall_models
from db.wzcard import models as wzcard_models
import datetime

import settings
import redis
from util.webapp_id2nickname import get_nickname_from_webapp_id
from util import msg_crypt

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_COMMON_DB)

crypt = msg_crypt.MsgCrypt(settings.WZCARD_ENCRYPT_INFO['token'], settings.WZCARD_ENCRYPT_INFO['encodingAESKey'],
                           settings.WZCARD_ENCRYPT_INFO['id'])


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

	@classmethod
	def __encrypt_password(cls, raw_password):
		password = str(raw_password)
		return crypt.EncryptMsg(password)

	@classmethod
	def __decrypt_password(cls, encrypt_password):
		return crypt.DecryptMsg(encrypt_password)[1]

	@staticmethod
	@param_required(['wzcard_info', 'money', 'order_id', 'webapp_user', 'webapp_owner'])
	def use(args):
		wzcard_info = args['wzcard_info']

		webapp_owner = args['webapp_owner']
		order_id = args['order_id']
		webapp_user = args['webapp_user']

		if webapp_user.member.is_subscribed:
			if mall_models.Order.select().dj_where(webapp_user_id=webapp_user.id).count() > 0:
				customer_type = 0
			else:
				customer_type = 1
		else:
			customer_type = 2

		params = {
			'card_infos': json.dumps(wzcard_info),
			'money': args['money'],
			'valid_money': -1,
			'order_id': order_id,
			'shop_id': webapp_owner.id,
			'shop_name': webapp_owner.user_profile.store_name,
			'customer_id': args['webapp_user'].member.id,
			'customer_type': customer_type
		}
		resp = Resource.use('card_apiserver').post({
			'resource': 'card.trade',
			'data': params
		})

		data = {}

		if resp:
			code = resp['code']
			data = resp['data']
			if code == 200:
				can_use = True
				msg = ''
			else:
				can_use = False
				msg = data['reason']
		else:
			can_use = False
			msg = u'系统繁忙'
			data['type'] = 'common:wtf'

		if can_use:
			mall_models.OrderCardInfo.create(
				order_id=order_id,
				trade_id=data['trade_id'],
				used_card=data['used_cards']
			)

		return can_use, msg, data

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
				if data['type'] in ('wzcard:nosuch', 'wzcard:wrongpass'):
					r.incr(times_key)
					if not r.ttl(times_key) > 0:
						r.expire(times_key, 86400)
				return False, data['type'], None
			else:

				# 判断是否绑定过
				if wzcard_models.MemberHasWeizoomCard.select().dj_where(member_id=member_id,
				                                                        card_number=card_number).count() > 0:
					# r.incr(times_key)
					# if not r.ttl(times_key) > 0:
					# 	r.expire(times_key, 86400)
					return False, 'wzcard:has_bound', None

				# 判断余额是否为0
				if float(data['balance']) == 0:
					# r.incr(times_key)
					# if not r.ttl(times_key) > 0:
					# 	r.expire(times_key, 86400)
					return False, 'wzcard:exhausted', None


				else:
					# 绑卡
					wzcard_models.MemberHasWeizoomCard.create(
						member_id=member_id, member_name='',
						card_number=card_number, card_password=WZCard.__encrypt_password(card_password),
						relation_id='',
						source=wzcard_models.WEIZOOM_CARD_SOURCE_BIND
					)

					get_card_infos_resp = WZCard.get_card_infos({
						'card_infos': [{'card_number': card_number, 'card_password': card_password}]
					})

					if not get_card_infos_resp:
						return False, 'common:wtf', None

					# 获得详细数据
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
		card_numbers_passwords = [
			{'card_number': a.card_number, 'card_password': WZCard.__decrypt_password(a.card_password)} for a in
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

	@staticmethod
	@param_required(['card_numbers', 'webapp_user'])
	def get_by_card_numbers(args):
		card_numbers = args['card_numbers']

		member_id = args['webapp_user'].member.id
		member_has_cards = wzcard_models.MemberHasWeizoomCard.select().dj_where(member_id=member_id,
		                                                                        card_number__in=card_numbers)
		# 保证顺序
		card_index = {card_number: index for index, card_number in enumerate(card_numbers)}
		member_has_cards = sorted(member_has_cards, key=lambda x: card_index[x.card_number])

		# usable_wzcard_info = [{a.card_number: a.card_password} for a in member_has_cards]
		usable_wzcard_info = [
			{'card_number': a.card_number, 'card_password': WZCard.__decrypt_password(a.card_password)} for a in
			member_has_cards]

		return usable_wzcard_info

	@staticmethod
	@param_required(['order_id', 'trade_id'])
	def refund(args):
		"""
		微众卡退款，取消订单或者下单失败时使用
		"""
		# 交易类型（支付失败退款：0、普通退款：1）
		if mall_models.Order.select().dj_where(order_id=args['order_id']).first():
			trade_type = 1
		else:
			trade_type = 0
		data = {
			'trade_id': args['trade_id'],
			'trade_type': trade_type
		}

		resp = Resource.use('card_apiserver').delete(
			{
				'resource': 'card.trade',
				'data': data
			}
		)

		is_success = resp and resp['code'] == 200

		return is_success

	@staticmethod
	@param_required(['webapp_user', 'webapp_owner', 'card_num'])
	def from_member_card_num(args):
		"""
		MemberHasWeizoomCard models的id 
		通过card_num获取微众卡的卡详情
		"""

		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		member_id = webapp_user.member.id
		card_num = args['card_num']
		print ">>>>>"*10
		print "webapp_user.openid:wzcard",webapp_user.openid
		print ">>>>>"*10
		member_has_cards = wzcard_models.MemberHasWeizoomCard.select().dj_where(member_id=member_id, card_number=card_num)
		# 卡详情和卡的购物信息
		card_detail = {}
		weizoom_card_orders_list = []
		# 卡详情和卡的购物信息
		if member_has_cards:
			card_numbers_passwords = [
				{'card_number': a.card_number, 'card_password': WZCard.__decrypt_password(a.card_password)} for a in
				member_has_cards]

			resp = WZCard.get_card_infos({
				'card_infos': card_numbers_passwords
			})

			if resp:
				card_infos = resp['data']['card_infos']
				for card in card_infos:
					card_detail = card.values()[0]

			param = {'card_infos': json.dumps(card_numbers_passwords)}
			resp = Resource.use('card_apiserver').post({
				'resource': 'card.get_cards_use_info',
				'data': param
			})

			if resp:
				card_infos = resp['data']['card_infos']
				if card_infos:
					card_has_orders = card_infos[0][card_numbers_passwords[0]['card_number']]['orders']
				# card_has_orders.reverse()

					if card_has_orders:
						order_nums = [co['order_id'] for co in card_has_orders]
						orders = mall_models.Order.select().dj_where(order_id__in=order_nums)
						order_id2webapp_id = dict([(order.order_id,order.webapp_id) for order in orders])

						for card_has_order in card_has_orders:
							webapp_id = order_id2webapp_id.get(card_has_order['order_id'])

							#webapp_id = order.webapp_id
							if webapp_id:
								key = "webapp_id2nickname_%s" % webapp_id
								nickname = cache_util.get_from_cache(key, get_nickname_from_webapp_id(key, webapp_id))
							else:
								nickname = ""
							weizoom_card_orders_list.append({
								'created_at': card_has_order['created_at'],
								'money': card_has_order['money'],
								'order_id': card_has_order['order_id'],
								"nickname": nickname
							})
			card_detail['use_details'] = weizoom_card_orders_list

		return card_detail
