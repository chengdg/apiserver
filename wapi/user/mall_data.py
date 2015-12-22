# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required

#import resource

class MallData(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'user'
	resource = 'mall_data'

	@param_required(['woid'])
	def get(args):
		"""
		创建商品
		"""
		mall_data = resource.get('account', 'mall_data', {
			"woid": args['woid']
		})
		return mall_data