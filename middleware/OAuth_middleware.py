# -*- coding: utf-8 -*-

from db.account import models as account_models
import resource
from business.account.webapp_owner import WebAppOwner
from business.account.member import Member
from business.account.webapp_user import WebAppUser
# from business.account.social_account_info import SocialAccountInfo
from utils import msg_crypt,auth_util
import settings
import logging

import  falcon 

from utils import error_codes

from core import redirects


class OAuthMiddleware(object):
	"""
	获取OAuthMiddlewarer的中间件微信授权

	@note 微信授权
	"""
	def process_request(sel, req, resp):
		
		if '/oauthserver' not in req.path:
			return 
		print '>>>>>>>>>>>>>>>212121'
		raise redirects.HTTPFound('http://www.baidu.com')

		# print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
		# #resp.location = 'http://www.baidu.com'
		# return resp.redirect()

		# args = req.params
		# try:
		# 	user = account_models.User.get(id=woid)
		# except:
		# 	return {"errorcode": error_codes.ILLEGAL_WOID_CODE, "errmsg": error_codes.code2msg[error_codes.ILLEGAL_WOID_CODE]}

		# #验证callback
		# if not args.has_key('callback_uri'):
		# 	return {"errorcode": error_codes.LACK_CALLBACK_URI, "errmsg": error_codes.code2msg[error_codes.LACK_CALLBACK_URI]}	
		
		# webapp_owner = WebAppOwner.get({
		# 	'woid': woid
		# })

		# mp_access_token = webapp_owner.weixin_mp_user_access_token

		# code = args.get('code', None)
		# appid = args.get('appid', None)
		# component_info = settings.COMPONENT_INFO
		# if not code or not appid:
		# 	"""
		# 		使用微信网页授权
		# 	"""
		# 	weixin_auth_url = 'https://open.weixin.qq.com/connect/oauth2/authorize' \
		# 	+ '?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=123&component_appid=%s#wechat_redirect' \
		# 	% (weixin_mp_user_access_token.app_id, urllib.quote(req.url).replace('/','%2F'), api_style, component_info.app_id)

		# 