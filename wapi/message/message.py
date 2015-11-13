# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required

import resource


class Message(api_resource.ApiResource):
	"""
	
	"""
	app = 'message'
	resource = 'message_messages'


	@param_required(['type', 'openid', 'appid', 'content'])
	def post(args):
		"""
		
		"""
		return resource.post('message', 'message_messages', {
			"type": args['type'],
			"openid": args['openid'],
			"content": args['content'],
			"appid": args['appid']
		})

