
# -*- coding: utf-8 -*-

from urllib import quote
from eaglet.core import api_resource
from eaglet.core.cache import utils as cache_util

from eaglet.decorator import param_required
from util import auth_util

from db.account.models import User
from business.account.access_token import AccessToken as BusinessAccessToken
from business.account.webapp_owner import WebAppOwner

from business.member_card.member_card import MemberCard

import settings

class AccessToken(api_resource.ApiResource):
	"""
	member card
	"""
	app = 'member'
	resource = 'member_card'


	@param_required(['webapp_user'])
	def get(args):
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']

		member_card = MemberCard.from_member_id({'member_id': webapp_user.member.id, 
				'fill_options': {
					'with_price': False
				}})
		if member_card:
			data = member_card.to_dict()
			data['is_vip'] = True
			return data

		return {'is_vip': False}
