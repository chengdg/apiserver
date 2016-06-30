# -*- coding: utf-8 -*-



from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.wzcard.wzcardutil import WZCardUtil
from business.wzcard.wzcard import WZCard


class BindingCard(api_resource.ApiResource):
	app = 'wzcard'
	resource = 'binding_cards'

	@param_required(['is_all'])
	def get(args):
		webapp_user = args['webapp_user']

		is_all = int(args['is_all']) == 1




