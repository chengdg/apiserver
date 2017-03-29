# -*- coding: utf-8 -*-
"""@package business.third_party_pay.jinge_card
会员卡
"""
import json, requests, redis
from datetime import datetime

from eaglet.decorator import param_required
from eaglet.core import watchdog

import settings
from business import model as business_model
from db.third_party_pay import models as third_party_pay_models
from util import jinge_api_util

redis_db = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_COMMON_DB)
EXPIRE_SECONDS = 5 * 60  #存在redis中的验证码有效时间5分钟
class JinGeCard(business_model.Model):
	"""
	锦歌饭卡
	"""
	__slots__ = (
		'id',
		'owner_id',
		'member_id',
		'batch_id',
		'phone_number',
		'card_number',
		'card_password',
		'token',
		'name',
		'company',
		'mer_id',
		'term_id',
		'is_deleted',
		'created_at'
	)

	def __init__(self):
		business_model.Model.__init__(self)

	@staticmethod
	def from_model(model):
		jinge_card = JinGeCard()
		jinge_card._init_slot_from_model(model)

		return jinge_card

	@staticmethod
	def from_member_id(member_id):
		model = third_party_pay_models.JinGeCard.select().dj_where(member_id=member_id, is_deleted=False).first()
		if model:
			return JinGeCard.from_model(model)
		return None

	@staticmethod
	def from_phone_number(phone_number):
		model = third_party_pay_models.JinGeCard.select().dj_where(phone_number=phone_number, is_deleted=False).first()
		if model and model.card_number:
			return JinGeCard.from_model(model)
		return None

	def get_captcha(self, phone_number):
		return redis_db.get('captcha_%s' % phone_number)

	@property
	def balance(self):
		"""
		账户余额
		"""
		return jinge_api_util.get_balance(self.card_number, self.token)

	@property
	def is_active(self):
		"""
		有卡号代表意见绑定了饭卡，并且设置了支付密码后才是可用的
		"""
		return self.card_number and self.card_password

	def update_phone_captcha(self, phone_number, captcha):
		redis_db.setex('captcha_%s' % phone_number, captcha, EXPIRE_SECONDS)

	@staticmethod
	def create(owner_id, member_id, phone_number):
		if third_party_pay_models.JinGeCard.select().dj_where(owner_id=owner_id, member_id=member_id, is_deleted=False).count() == 0:
			return third_party_pay_models.JinGeCard.create(
				owner=owner_id,
				member_id=member_id,
				phone_number=phone_number
			)

	def bind(self, phone_number):
		#如果该手机号已经绑定过，则返回失败
		if JinGeCard.from_phone_number(phone_number):
			return False

		data = jinge_api_util.get_card_info_by_phone(phone_number)
		if data:
			third_party_pay_models.JinGeCard.update(
				card_number=data['card_number'], 
				token=data['token'],
				name=data['name'],
				company=data['company'],
				mer_id=data['mer_id'],
				term_id=data['term_id']
			).dj_where(owner_id=self.owner_id, member_id=self.member_id, phone_number=phone_number, is_deleted=False).execute()
			return True
		else:
			return False

	def set_password(self, password):
		if password:
			self.card_password = password
			third_party_pay_models.JinGeCard.update(
				card_password=password, 
			).dj_where(owner_id=self.owner_id, member_id=self.member_id, card_number=self.card_number, is_deleted=False).execute()
			return True
		return False

	def use(self, order_id, money):
		"""
		使用锦歌饭卡支付
		"""
		trade_time = datetime.now().strftime('%Y%m%d%H%M%S')
		is_success, trade_id = jinge_api_util.pay(self.card_number, self.card_password, self.token, money, self.mer_id, self.term_id, trade_time)
		if is_success:
			watchdog.info(u'use jinge_card: {}, order_id: {}, trade_id: {}, money: {}'.format(self.card_number, order_id, trade_id, money))
			third_party_pay_models.JinGeCardLog.create(
				jinge_card=self.id,
				price=money,
				trade_id=trade_id,
				order_id=order_id,
				reason=u"下单",
				balance=self.balance,
			)
		else:
			watchdog.alert(u'use jinge_card error: {}, order_id: {}, trade_id: {}, money: {}'.format(self.card_number, order_id, trade_id, money))

		return is_success, trade_id

	def refund(self, order_id, trade_id, money):
		"""
		锦歌饭卡退款，取消订单或者下单失败时使用
		"""
		is_success, refund_trade_id, trade_amount = jinge_api_util.refund(self.card_number, self.card_password, self.token, trade_id, order_id, money)
		if is_success:
			watchdog.info(u'refund jinge_card: {}, order_id: {}, trade_id: {}, money: {}'.format(self.card_number, order_id, refund_trade_id, trade_amount))
			third_party_pay_models.JinGeCardLog.create(
				jinge_card=self.id,
				trade_id=refund_trade_id,
				order_id=order_id,
				reason=u"取消下单或下单失败",
				balance=self.balance,
				price=trade_amount
			)
			
		return is_success