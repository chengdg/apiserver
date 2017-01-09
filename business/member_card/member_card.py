# -*- coding: utf-8 -*-
"""@package business.member_card.member_card
会员卡
"""
import json
import operator
from decimal import Decimal
from datetime import datetime

from eaglet.utils.resource_client import Resource
from eaglet.decorator import param_required
from db.member import models as member_models

from business import model as business_model
from db.mall import models as mall_models
import settings

from eaglet.core import watchdog
from util import msg_crypt

# r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_COMMON_DB)

crypt = msg_crypt.MsgCrypt(settings.WZCARD_ENCRYPT_INFO['token'], settings.WZCARD_ENCRYPT_INFO['encodingAESKey'],
                           settings.WZCARD_ENCRYPT_INFO['id'])
CAN_USE_TEXT = u'可用'  #card_apiserver中定义的微众卡可用状态的文本

class MemberCard(business_model.Model):
	"""
	会员卡
	"""
	__slots__ = (
		'id',
		'member_id',
		'batch_id',
		'card_number',
		'card_password',
		'card_name',
		'created_at',
		'balance',
		'is_active',  #会员卡状态
		'remained_backcash_times',   #剩余返现次数
		'valid_time_to',
		'interval_days',  #返款间隔天数
		'next_clear_time'  #本期余额下次清空时间
	)

	def __init__(self, model):
		business_model.Model.__init__(self)

		self.context['db_model'] = model

	@staticmethod
	@param_required(['model'])
	def from_model(args):
		"""
		工厂对象，根据MemberCard model获取MemberCard业务对象

		@param[in] model: MemberCard model

		@return MemberCard业务对象
		"""
		fill_options = args.get("fill_options", {})

		model = args['model']


		member_card = MemberCard(model)
		member_card._init_slot_from_model(model)
		member_card.balance = 0
		member_card.is_active = False
		member_card.remained_backcash_times = 0
		member_card.interval_days = 0
		member_card.next_clear_time = ''
		MemberCard.fill_options(member_card, fill_options)

		return member_card

	@staticmethod
	@param_required(['member_id'])
	def from_member_id(args):
		model = member_models.MemberCard.select().dj_where(member_id=args['member_id']).first()
		fill_options = args.get('fill_options', {})
		if model:
			return MemberCard.from_model({
				"model": model,
				"fill_options": fill_options
				})
		return None

	def get_bill_info(self):
		"""
		获取会员卡的账单信息
		"""
		bill_info = []
		#会员卡的消费和待支付订单变为已取消订单时的退款记录
		order_related_records = member_models.MemberCardLog.select().dj_where(member_card_id=self.id)
		for record in order_related_records:
			#todo 把行为转换成便于在手机端显示的描述
			action = record.reason
			price = record.price
			if record.reason == u'下单':
				action = u'支付订单：%s' % record.order_id
				price = 0 - record.price  #消费的金额使用负数显示
			if record.reason == u'取消下单或下单失败':
				action = u'订单退款：%s' % record.order_id

			bill_info.append({
				'action': action,
				'money': price,
				'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
			})
		
		#从微众卡系统获取充值和清零记录
		resp = Resource.use('card_apiserver').get({
				'resource': 'card.recharge_infos',
				'data': {'card_number': self.card_number}
			})
		if resp:
			code = resp['code']
			recharge_infos = resp['data']['recharge_infos']
			if code == 200:
				for info in recharge_infos:
					money = info['recharge_money']
					if money == 0:
						continue
					is_auto = info['is_auto']
					action = ''
					if is_auto == 1:
						if money > 0:
							action = u'会员卡第%s期系统充值' % info['phase']
						if money < 0:
							action = u'会员卡第%s期余额到期' % info['phase']
					else:
						action = u'人工充值'

					bill_info.append({
						'action': action,
						'money': money,
						'created_at': info['created_at']
					})
			else:
				watchdog.error(resp)

		#按时间倒序
		bill_info.sort(key=operator.itemgetter('created_at'),reverse=True)

		#按月份分组
		current_month = []
		last_month = []
		earlier_month = []
		current_month_str = datetime.now().strftime("%Y-%m")
		last_month_str = get_last_month_str()
		for item in bill_info:
			if current_month_str in item['created_at']:
				current_month.append(item)
			elif last_month_str in item['created_at']:
				last_month.append(item)
			else:
				earlier_month.append(item)

		return {
			'current_month': current_month,
			'last_month': last_month,
			'earlier_month': earlier_month
		}
		

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'batch_id', 'card_number', 'card_password', 'card_name'])
	def create(args):
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		member_id = webapp_user.member.id
		if member_models.MemberCard.select().dj_where(owner_id=webapp_owner.id, member_id=member_id, is_active=True).count() == 0:
			return member_models.MemberCard.create(
				owner_id=webapp_owner.id,
				member_id=member_id,
				batch_id=args['batch_id'],
				card_number=args['card_number'],
				card_password=args['card_password'],
				card_name=args['card_name']
			)


	@staticmethod
	def fill_options(member_card, fill_options):
		if fill_options:
			with_price = fill_options.get("with_price", False)
			#member_card.balance = 100
			if with_price:
				member_card.balance = 0
				#访问微众卡service
				wzcard_info = [{
					"card_number": member_card.card_number,
					"card_password": member_card.card_password
				}]
				params = {
					'card_infos': json.dumps(wzcard_info),
					
				}
				resp = Resource.use('card_apiserver').post({
					'resource': 'card.get_cards',
					'data': params
				})

				data = {}

				if resp:
					code = resp['code']
					data = resp['data']
					if code == 200:
						card_infos = resp['data']['card_infos']
						if len(card_infos) == 1:
							#判断微众卡状态是否可用 duhao
							card_status_text = card_infos[0][member_card.card_number]['status']
							if card_status_text == CAN_USE_TEXT:
								member_card.is_active = True
							#剩余返现次数
							remained_backcash_times = card_infos[0][member_card.card_number]['membership_to_recharge_times']
							member_card.remained_backcash_times = remained_backcash_times
							member_card.valid_time_to = card_infos[0][member_card.card_number]['valid_time_to']
							member_card.balance = card_infos[0][member_card.card_number]['balance']
							member_card.next_clear_time = card_infos[0][member_card.card_number]['next_clear_time']
					else:
						watchdog.error(resp)

				batch_info = get_batch_info(member_card.batch_id)
				member_card.interval_days = int(Decimal(batch_info.get('vip_back_via_day', 30)))

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
			member_models.MemberCardLog.create(
				member_card=webapp_user.member_card.id,
				trade_id=data['trade_id'],
				order_id=order_id,
				reason=u"下单",
				# price=float(args['money'])
				price=float(data['paid_money'])
			)

		return can_use, msg, data


	@staticmethod
	@param_required(['order_id', 'trade_id', 'member_card_id', 'price'])
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
		if is_success:
			try:
				log = member_models.MemberCardLog.select().dj_where(order_id=args['order_id'],reason=u'下单').first()
				member_models.MemberCardLog.create(
					member_card=args['member_card_id'],
					trade_id=args['trade_id'],
					order_id=args['order_id'],
					reason=u"取消下单或下单失败",
					price=log.price
				)
			except Exception, e:
				watchdog.error(u'会员卡自动退款时获取下单时的扣除金额失败,member_card_id:%s,order_id:%s' % (args['member_card_id'], args['order_id']))
				watchdog.error(e)
			
		return is_success

	@classmethod
	def encrypt_password(raw_password):
		password = str(raw_password)
		return crypt.EncryptMsg(password)

	@classmethod
	def decrypt_password(cls, encrypt_password):
		return crypt.DecryptMsg(encrypt_password)[1]


def get_batch_info(batch_id):
	"""
	根据batch_id获取单个批次卡的详细信息
	"""
	batch_info = None
	resp = Resource.use('card_apiserver').get({
				'resource': 'card.membership_batch',
				'data': {'membership_batch_id': batch_id}
			})
	if resp:
		code = resp['code']
		data = resp['data']['card_info']
		if code == 200:
			batch_info = data
		else:
			watchdog.error(resp)

	return batch_info


def get_last_month_str():
	today = datetime.today()
	year = today.year
	month = today.month
	if month == 1:
		month = 12
		year -= 1
	else:
		month -= 1

	return datetime(year, month, 1).strftime("%Y-%m")