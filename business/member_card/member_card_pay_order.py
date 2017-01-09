# -*- coding: utf-8 -*-
"""@package business.member_card.member_card_pay_order
会员卡支付订单
"""
import json
from datetime import datetime
from decimal import Decimal

from eaglet.utils.resource_client import Resource
from eaglet.decorator import param_required
from eaglet.core import watchdog

from business.mall.pay_interface import PayInterface
from business import model as business_model
from db.member import models as member_models
from db.mall import models as mall_models
from member_card import MemberCard, get_batch_info

class MemberCardPayOrder(business_model.Model):
	"""
	会员卡支付订单
	"""
	__slots__ = (
		'id',
		'owner_id',
		'member_id',
		'batch_id',
		'order_id',
		'batch_name',
		'price',
		'is_paid',
		'created_at',
		'paid_at'
	)

	def __init__(self, model, webapp_owner=None, webapp_user=None):
		business_model.Model.__init__(self)

		if model:
			self._init_slot_from_model(model)
		if webapp_owner:
			self.context['webapp_owner'] = webapp_owner
		if webapp_user:
			self.context['webapp_user'] = webapp_user

	@staticmethod
	@param_required(['order_id'])
	def from_order_id(args):
		"""工厂方法，根据支付接口类型创建PayInterface对象

		@param [in] pay_interface_type : 支付接口的类型

		@return PayInterface业务对象
		"""

		order_id = args['order_id']
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']

		model = member_models.MemberCardPayOrder.select().dj_where(owner_id=webapp_owner.id, member_id=webapp_user.member.id, order_id=order_id).first()
		pay_order = MemberCardPayOrder(model, webapp_owner, webapp_user)
		return pay_order

	@staticmethod
	@param_required(['owner_id', 'member_id', 'batch_id', 'order_id', 'batch_name', 'price'])
	def get_member_card_pay_order(args):
		"""
		工厂对象，根据MemberCard model获取MemberCard业务对象

		@param[in] model: MemberCard model

		@return MemberCard业务对象
		"""
		member_card_pay_order, created = member_models.MemberCardPayOrder.get_or_create(
					owner_id=args['owner_id'], 
					member_id=args['member_id'], 
					batch_id=args['batch_id'],
					order_id=args['order_id'],
					batch_name=args['batch_name'],
					price=args['price'],
					is_paid=False
				)

		#如果一个会员点击过开通会员，但是没有支付，然后商家更改了会员卡的价格，那么就需要
		#把数据库中已经存储的价格改成最新的
		if not created and args['price'] != member_card_pay_order.price:
			member_card_pay_order.price = args['price']
			member_card_pay_order.save()

		return MemberCardPayOrder(member_card_pay_order)


	def pay_info_for_pay_module(self, pay_interface_type):
		"""
		用于pay模块的订单支付信息
		@return:
		"""
		if not self.is_paid:
			pay_interface = PayInterface.from_type({
				"webapp_owner": self.context['webapp_owner'],
				"pay_interface_type": pay_interface_type
			})
			pay_info = pay_interface.get_order_pay_info_for_pay_module(None)
			
			pay_info['final_price'] = self.price
			pay_info['is_status_not'] = True
			pay_info['order_id'] = self.order_id
			pay_info['woid'] = self.context['webapp_owner'].id
			pay_info['product_price'] =self.price
			pay_info['product_names'] = self.batch_name
			return pay_info
		else:
			return {
				'is_status_not': False,
				'woid': self.context['webapp_owner'].id
			}

	def wx_package_for_pay_module(self,config):
		wx_package_info ={}
		wx_package_info['woid'] = self.context['webapp_owner'].id

		if not config:
			wx_package_info['product_names'] = self.batch_name
			wx_package_info['total_fee'] = int(Decimal(str(self.price)) * 100)

		pay_interface = PayInterface.from_type({
			"webapp_owner": self.context['webapp_owner'],
			"pay_interface_type": mall_models.PAY_INTERFACE_WEIXIN_PAY
		})

		wx_package = pay_interface.wx_package_for_pay_module()

		wx_package_info.update(wx_package)
		return wx_package_info


	def pay(self):
		if not self.is_paid:
			now = datetime.now()
			member_models.MemberCardPayOrder.update(is_paid=True, paid_at=now).dj_where(order_id=self.order_id).execute()

			params = {
				'weizoom_card_batch_id': self.batch_id,
				'sold_time': now.strftime('%Y-%m-%d %H:%M:%S'),
				'member_id': self.member_id,
				'phone_num': self.context['webapp_user'].phone_number
			}
			resp = Resource.use('card_apiserver').get({
				'resource': 'card.membership_card',
				'data': {'card_condition': json.dumps(params)}
			})

			if resp:
				code = resp['code']
				data = resp['data']
				if code == 200:
					card_number = data['card_number']
					card_password = data['card_password']

					args = {
						'webapp_owner': self.context['webapp_owner'],
						'webapp_user': self.context['webapp_user'],
						'batch_id': self.batch_id,
						'card_number': card_number,
						'card_password': card_password,
						'card_name': self.batch_name
					}
					member_card = MemberCard.create(args)

					batch_info = get_batch_info(self.batch_id)
					member_models.MemberCardLog.create(
						member_card=member_card.id,
						reason=u"开通会员卡充值",
						price=batch_info['first_money']
					)
				else:
					watchdog.error(resp)