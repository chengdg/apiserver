# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
from utils import auth_util

class AccessToken(api_resource.ApiResource):
	"""
	access_token
	"""
	app = 'user'
	resource = 'access_token'

	@param_required(['webapp_owner_id', 'openid'])
	def get(args):
		"""
		获取access_token
		"""
		webapp_owner_id = args['webapp_owner_id']
		openid = args['openid']

		"""
		TODO:
			1、验证 webapp_owner_id 和 openid是有效
		"""
		if not webapp_owner_id:
			raise 'error webapp_owner_id'

		if not openid:
			raise 'error openid'				
		access_token = auth_util.encrypt_access_token(str(webapp_owner_id), openid)
		return {
			"access_token": access_token
		}
