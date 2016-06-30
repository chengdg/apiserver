# -*- coding: utf-8 -*-



from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.wzcard.wzcardutil import WZCardUtil
from business.wzcard.wzcard import WZCard


class ABindingCard(api_resource.ApiResource):
	app = 'wzcard'
	resource = 'binding_cards'

	@param_required(['is_all'])
	def get(args):
		webapp_user = args['webapp_user']

		is_all = int(args['is_all']) == 1

		if webapp_user.wzcard_package.is_valid:

			if is_all:
				return {
					'usable_cards': [card.to_dict() for card in webapp_user.wzcard_package.usable_cards],
					'unusable_cards': [card.to_dict() for card in webapp_user.wzcard_package.unusable_cards]
				}
			else:
				return {
					'usable_cards': [card.to_dict() for card in webapp_user.wzcard_package.usable_cards],
				}
		else:
			return 500, {'type': 'common:wtf'}
