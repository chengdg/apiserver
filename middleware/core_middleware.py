# -*- coding: utf-8 -*-

class ApiAuthMiddleware(object):
	def process_request(self, req, resp):
		print 'in api auth middleware...'