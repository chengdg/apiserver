# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
#from wapi.wapi_utils import create_json_response


class Token(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'user'
	resource = 'token'

	@param_required(['wuid'])
	def put(args):
		"""
		创建商品
		"""
		return {
			"token": '%s_token' % args['wuid']
		}
