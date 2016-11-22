# -*- coding: utf-8 -*-
"""@package business.account.member_card
会员卡
"""

from eaglet.decorator import param_required
from db.member import models as member_models

from business import model as business_model
import settings


class MemberCard(business_model.Model):
	"""
	会员卡
	"""
	__slots__ = (
		'id',
		'member_id',
		'card_number',
		'card_password',
		'type',
		'card_name',
		'created_at'
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
		model = args['model']

		integral = MemberCard(model)
		integral._init_slot_from_model(model)
		return integral

	@staticmethod
	@param_required(['member_id'])
	def from_member_id(args):
		model = member_models.MemberCard.select().dj_where(member_id=args['member_id']).first()

		if model:
			return MemberCard.from_model({
				"model": model
				})
		return None