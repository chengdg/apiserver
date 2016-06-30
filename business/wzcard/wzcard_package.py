# # -*- coding: utf-8 -*-
#
#

from eaglet.decorator import param_required

import db.wzcard.models as wzcard_models
from business import model as business_model
from business.wzcard.wzcard import WZCard


class WZCardPackage(business_model.Model):
	__slots__ = (

		'unusable_cards',
		'usable_cards',
		'is_valid'

	)

	def __init__(self, webapp_user):
		self.__fill_cards(webapp_user)

	def __fill_cards(self, webapp_user):
		member_id = webapp_user.member.id

		member_has_cards = wzcard_models.MemberHasWeizoomCard.select().dj_where(member_id=member_id)
		is_success, self.usable_cards, self.unusable_cards = WZCard.from_member_has_cards(
			{'member_has_cards': member_has_cards})

		if is_success:
			self.is_valid = True
		else:
			self.is_valid = False



	@staticmethod
	@param_required(['webapp_user', 'card_number', 'card_password'])
	def bind_card(arg):
		pass

	@staticmethod
	@param_required(['webapp_user'])
	def from_webapp_user(args):
		webapp_user = args['webapp_user']
		return WZCardPackage(webapp_user)
