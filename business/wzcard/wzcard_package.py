# -*- coding: utf-8 -*-


import json

from eaglet.decorator import param_required

import db.wzcard.models as wzcard_models
import settings
from eaglet.utils.api_resource import APIResourceClient
from business import model as business_model


class WZCardPackage(business_model):
	__slots__ = (

	)

	@staticmethod
	@param_required(['webapp_user', 'card_number', 'card_password'])
	def bind_card(arg):
		pass

	@staticmethod
	@param_required(['webapp_user'])
	def get_package_by_webapp_user(args):
		webapp_user = args['webapp_user']

		member_id = webapp_user.member.id

		card_models = wzcard_models.MemberHasWeizoomCard.select().dj_where(member_id=member_id)
