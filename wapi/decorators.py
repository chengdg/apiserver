#coding: utf8
"""
WAPI检查是否有权限的decorator

"""

#from functools import wraps
#from django.utils.decorators import available_attrs

#from core.jsonresponse import create_response

class ApiParamaterError(Exception):
	pass


def param_required(params=None):
	def wrapper(function):
		def inner(data):
			for param in params:
				if not param in data:
					raise ApiParamaterError('Required parameter missing: %s' % param)
			return function(data)
		return inner 
	return wrapper
