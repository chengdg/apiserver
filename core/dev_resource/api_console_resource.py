# -*- coding: utf-8 -*-
import os
import falcon

import settings
from core import api_resource

class ApiConsoleResource:
	"""
	返回api console页面
	"""
	def __init__(self):
		pass

	def on_get(self, req, resp):
		resources = [resource.replace('-', '.') for resource in api_resource.APPRESOURCE2CLASS.keys()]
		resources.sort()
		options = ['<option value="%s">%s</option>' % (resource, resource) for resource in resources]

		resp.content_type = 'text/html'
		resp.status = falcon.HTTP_200  # This is the default status
		console_file_path = os.path.join(settings.PROJECT_HOME, 'static/api_console.html')
		src = open(console_file_path)
		content = src.read()
		content = content.replace('{{ resources }}', '\n'.join(options))
		src.close()
		resp.body = content 