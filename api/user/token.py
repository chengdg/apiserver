# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
#from api.wapi_utils import create_json_response


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
