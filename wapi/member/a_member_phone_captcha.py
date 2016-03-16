# -*- coding: utf-8 -*-

import urllib
import urlparse
from core import api_resource
from wapi.decorators import param_required
from utils import send_phone_msg
from business.account.webapp_user import WebAppUser

class AMemberPhoneCaptcha(api_resource.ApiResource):
	"""
	会员
	"""
	app = 'member'
	resource = 'member_phone_captcha'


	@param_required(['webapp_owner', 'webapp_user','phone_number', 'sessionid'])
	def get(args):
		"""
		获取手机验证码

		@param
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		phone_number = args['phone_number']
		sessionid = args['sessionid']
		data = {}
		if webapp_user.is_binded is False:
			if WebAppUser.can_binding_phone(webapp_owner.webapp_id, phone_number):
				company_name = webapp_owner.mpuser_preview_info.name
				result,captcha = send_phone_msg.send_captcha(phone_number,company_name)
				if result and captcha:
					sucess = webapp_user.update_phone_captcha(phone_number, captcha, sessionid, webapp_owner.webapp_id)
					if sucess:
						return {"captcha": captcha}
					else:
						return 503, u'手机已经被绑定过'
				else:
					return 502, u'获取手机验证码失败'
			else:
				return 503, u'手机已经被绑定过'
		else:
			return 501, u'会员已经绑定过手机'


	