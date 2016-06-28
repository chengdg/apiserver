# -*- coding: utf-8 -*-



from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.wzcard.wzcardutil import WZCardUtil


class BindingCard(api_resource.ApiResource):
	app = 'wzcard'
	reource = 'binding_card'

	@param_required(['card_number', 'card_password'])
	def put(args):
		pass