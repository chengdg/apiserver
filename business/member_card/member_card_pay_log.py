# -*- coding: utf-8 -*-
"""@package business.member_card.member_card_pay_log
会员卡支付记录
"""
import json
from eaglet.utils.resource_client import Resource
from eaglet.decorator import param_required

from business import model as business_model
from db.member import models as member_models

from eaglet.core import watchdog

class MemberCardPayLog(business_model.Model):
	"""
	会员卡
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

	def __init__(self, model):
		business_model.Model.__init__(self)

		if model:
			self._init_slot_from_model(model)

	@staticmethod
	@param_required(['owner_id', 'member_id', 'batch_id', 'order_id', 'batch_name', 'price', 'is_paid'])
	def get_member_card_pay_log(args):
		"""
		工厂对象，根据MemberCard model获取MemberCard业务对象

		@param[in] model: MemberCard model

		@return MemberCard业务对象
		"""
		member_card_pay_log, created = member_models.MemberCard.get_or_create(
					owner_id=args['owner_id'], 
					member_id=args['member_id'], 
					batch_id=args['batch_id'],
					order_id=args['order_id'],
					batch_name=args['batch_name'],
					price=args['price'],
					is_paid=False
				)

		return MemberCardPayLog(member_card_pay_log)