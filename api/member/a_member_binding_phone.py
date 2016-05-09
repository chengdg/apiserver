# -*- coding: utf-8 -*-

import urllib
import urlparse
from eaglet.core import api_resource
from eaglet.decorator import param_required
from util import url_helper

class AMemberBindingPhone(api_resource.ApiResource):
	"""
	会员
	"""
	app = 'member'
	resource = 'member_binding_phone'

	# @param_required(['webapp_user'])
	# def get(args):
	# 	"""
	# 	获取会员详情

	# 	@param
	# 	"""
	# 	webapp_user = args['webapp_user']
		
	# 	webapp_user.phone


	# 	return {"phone_number": webapp_user.phone}


	@param_required(['webapp_owner', 'webapp_user','phone_number', 'captcha', 'sessionid'])
	def put(args):
		"""
		绑定手机

		@param
		"""
		webapp_user = args['webapp_user']
		phone_number = args['phone_number']
		webapp_owner = args['webapp_owner']
		captcha = args['captcha']
		sessionid = args['sessionid']
		print phone_number,'>>>>>>>', webapp_user.phone_number
		if phone_number != webapp_user.phone_number:
			return 500, u'手机号错误'
		elif captcha != webapp_user.captcha or len(captcha) != 4:
			return 500, u'验证码错误'
		elif sessionid != webapp_user.captcha_session_id:
			return 500, u'captcha_session_id error'
		else:
			webapp_user.binded

		

		return {"phone_number": phone_number}