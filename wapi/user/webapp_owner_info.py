# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required

import resource

class WebAppOwnerInfo(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'user'
	resource = 'webapp_owner_info'

	@param_required(['woid'])
	def get(args):
		"""
		创建商品
		"""
		_, webapp_owner_info_dict = resource.get('account', 'webapp_owner_info', {
			"woid": args['woid']
		})
		return webapp_owner_info_dict