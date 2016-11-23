# -*- coding: utf-8 -*-
"""@package business.account.member_card
会员卡
"""

from eaglet.decorator import param_required
from db.member import models as member_models

from business import model as business_model
import settings

from eaglet.core import watchdog

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
		'created_at',
		'balance'
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


	@staticmethod
	def fill_options(member_card, fill_options):
		if fill_options:
			with_price = fill_options.get("with_price", False)
			member_card.balance = 100
			# if with_price:
			# 	#访问微众卡service
			# 	wzcard_info = [{
			# 		"card_number": member_card.card_number,
			# 		"card_password": member_card.card_password
			# 	}]
			# 	params = {
			# 		'card_infos': json.dumps(wzcard_info),
					
			# 	}
			# 	resp = Resource.use('card_apiserver').post({
			# 		'resource': 'card.get_cards',
			# 		'data': params
			# 	})

			# 	data = {}

			# 	if resp:
			# 		code = resp['code']
			# 		data = resp['data']
			# 		if code == 200:
			# 			card_infos = resp['data']['card_infos']
			# 			if len(card_infos) == 1:
			# 				member_card.balance = card_infos[0]['balance']
			# 			else:
			# 				member_card.balance = 0
			# 		else:
			# 			watchdog.error(resp)
			# 	else:
			# 		member_card.balance = 0