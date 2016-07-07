# -*- coding: utf-8 -*-



from eaglet.core import api_resource
from eaglet.decorator import param_required


class ABindingCard(api_resource.ApiResource):
	app = 'wzcard'
	resource = 'binding_cards'

	@param_required([])
	def get(args):
		webapp_user = args['webapp_user']

		if webapp_user.wzcard_package.is_valid:

			return {
				'usable_cards': [card.to_dict() for card in webapp_user.wzcard_package.usable_cards],
				'unusable_cards': [card.to_dict() for card in webapp_user.wzcard_package.unusable_cards]
			}


		else:
			return 500, {'type': 'common:wtf'}
