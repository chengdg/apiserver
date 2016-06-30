# # -*- coding: utf-8 -*-
#
#
import json

from eaglet.decorator import param_required

import db.wzcard.models as wzcard_models
import settings
from eaglet.utils.api_resource import APIResourceClient
from business import model as business_model
from eaglet.decorator.decorator import cached_context_property
from eaglet.utils.resource_client import Resource

from business.wzcard.wzcard import WZCard


# class WZCardPackage(business_model):
# 	__slots__ = (
# 		'cards',
# 		'member_id',
# 		'webapp_owner_id'
# 		'webapp_user_id'
#
# 	)
#
# 	def __init__(self, webapp_user):
# 		pass
# 		member_id = webapp_user.member.id
#
# 		self.__fill_cards(webapp_user)
#
# 	def __fill_cards(self, webapp_user):
# 		member_id = webapp_user.member.id
#
# 		member_has_cards = wzcard_models.MemberHasWeizoomCard.select().dj_where(member_id=member_id)
# 		self.cards = WZCard.from_member_has_cards({'member_has_cards': member_has_cards})

	# @cached_context_property
	# def cards(self):
	# 	pass

	# @staticmethod
	# @param_required(['webapp_owner', 'webapp_user', 'card_number', 'card_password'])
	# def check(args):
	# 	params = {
	# 		'card_number': args['card_number'],
	# 		'card_password': args['card_password'],
	# 		'exist_cards': json.dumps(args['exist_cards']),
	# 		'valid_money': args['valid_money'],  # 商品原价+运费
	# 	}
	#
	# 	params.update(self.__get_webapp_owner_info())
	# 	params.update(self.__get_webapp_user_info())
	#
	# @staticmethod
	# @param_required(['webapp_user', 'card_number', 'card_password'])
	# def bind_card(arg):
	# 	pass

	# @staticmethod
	# @param_required(['webapp_user'])
	# def from_webapp_user(args):
	# 	# webapp_user = args['webapp_user']
	# 	#
	# 	# member_id = webapp_user.member.id
	# 	#
	# 	# card_models = wzcard_models.MemberHasWeizoomCard.select().dj_where(member_id=member_id)
	# 	webapp_user = args['webapp_user']
	# 	return WZCardPackage(webapp_user)
