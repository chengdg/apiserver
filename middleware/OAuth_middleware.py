# -*- coding: utf-8 -*-

import json
import urllib
import urllib2
import  falcon 
import urlparse
from falcon.http_status import HTTPStatus

from db.account import models as account_models
from db.account import weixin_models
from business.account.webapp_owner import WebAppOwner
from business.account.system_account import SystemAccount
from business.spread.member_spread import MemberSpread
from core import redirects
from core.watchdog.utils import watchdog_alert, watchdog_warning, watchdog_error
from core.exceptionutil import unicode_full_stack
from utils import msg_crypt, auth_util, error_codes
import settings
#import resource

# from wapi.member import a_member_account
from wapi.user.access_token import AccessToken

class OAuthMiddleware(object):
	"""
	获取OAuthMiddlewarer的中间件微信授权

	@note 授权流程
		1、验证woid
		2、获取owner信息
		3、验证callback_uri
		4、通过微信oauth2网页授权接口获取code
		5、通过code获取openid
		6、通过openid创建并获取会员（如果callback_uri含有fmt处理分享url和会员关系）
		7、通过openid和woid获取access_toke信息
		8、回调callback_uri并且在url的querystring中增加access_token

		注：如果7无法获取正常会员帐号信息，会直接回调callback_uri
	"""
	def process_request(self, req, resp):
		
		if '/oauthserver' not in req.path:
			return 

		args = req.params
		woid = args.get('woid', None)
		# 验证woid
		if not woid:
			body = {"errorcode": error_codes.ILLEGAL_WOID_CODE, "errmsg": error_codes.code2msg[error_codes.ILLEGAL_WOID_CODE]}
			self.raise_response(body)
		# 获取owner信息
		webapp_owner = WebAppOwner.get({
			'woid': args['woid']
		})
		if not webapp_owner:
			body = {"errorcode": error_codes.ILLEGAL_WOID_CODE, "errmsg": error_codes.code2msg[error_codes.ILLEGAL_WOID_CODE]}
			self.raise_response(body)

		# 验证callback
		callback_uri = args.get('callback_uri', None)
		if not args.has_key('callback_uri'):
			body = {"errorcode": error_codes.LACK_CALLBACK_URI, "errmsg": error_codes.code2msg[error_codes.LACK_CALLBACK_URI]}	
			self.raise_response(body)
		
		# 获取公众号的access_token信息
		weixin_mp_user_access_token = webapp_owner.weixin_mp_user_access_token
		code = args.get('code', None)
		appid = args.get('appid', None)
		component_info = settings.COMPONENT_INFO
		if not code or not appid:
			"""
				使用微信网页授权
			"""
			#TODO-bert： 增加使用高级授权判断
			api_style = "snsapi_base"
			url = 'https://open.weixin.qq.com/connect/oauth2/authorize' \
			+ '?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=123&component_appid=%s#wechat_redirect' \
			% (weixin_mp_user_access_token.app_id, urllib.quote(req.url).replace('/','%2F'), api_style, component_info['app_id'])
		else:
			"""
				通过code获取openid，
				通过openid创建或者获取会员信息
				通过callbackuri信息创建会员关系
				通过会员信息获取access_token
			"""
			openid = self.get_openid_from(component_info, appid, code)
			if not openid:
				url = callback_uri
			else:
				apiserver_access_token = self.get_access_token_from(callback_uri, openid, webapp_owner)
				url = self.get_url(callback_uri, apiserver_access_token)
				#url = args['callback_uri'] + '&access_token=' + apiserver_access_token
		
		raise redirects.HTTPFound(str(url))

	def get_url(self, callback_uri, access_token):
		callback_uri = urllib.unquote(callback_uri)
		if callback_uri.find('?') > -1:
			callback_uri = callback_uri + '&access_token=' + access_token
		elif callback_uri.endswith('/'):
			callback_uri = callback_uri + '?access_token=' + access_token
		else:
			callback_uri = callback_uri + '/?access_token=' + access_token
		print '>>>>>>>.callback_uri:',callback_uri
		return callback_uri


	def get_access_token_from(self, callback_uri, openid, webapp_owner):
		"""
			@param[in] callback_uri
			@param[in] openid
			@param[in] webapp_owner

			@note 首先获取帐号，获取帐号异常则返回callback_uri
			@note 根据woid和openid获取access_token
		"""
		member_account = self.get_member_account(callback_uri, openid, webapp_owner)
		if not member_account:
			print 'a_member_account.AMemberAccount.prrocess_openid_for err'
			raise redirects.HTTPFound(str(callback_uri))

		access_token = AccessToken.put({
				'woid': webapp_owner.id,
				'openid': openid
				})

		return access_token['access_token']

	def get_member_account(self, callback_uri, openid, webapp_owner):
		"""
			@param[in] callback_uri
			@param[in] openid
			@param[in] webapp_owner

			@note 获取openid帐号信息，没有则创建
		"""
		member_account = MemberSpread.process_openid_for({
			'openid': openid,
			'for_oauth':'1',
			'url': callback_uri,
			'woid': webapp_owner.id,
			'webapp_owner': webapp_owner
			})

		system_account = SystemAccount.get({
			'webapp_owner': webapp_owner,
			'openid': openid
		})

		data = {}
		data['webapp_user'] = system_account.webapp_user.to_dict()
		data['social_account'] = system_account.social_account.to_dict()
		return data


	def get_openid_from(self, component_info, appid, code):
		"""
			@param[in] component_info 开放平台第三方帐号信息
			@param[in] openid 公众号唯一标识
			@param[in] webapp_owner 店铺信息

			@note 通过微信oauth2 api获取openid， 异常重试一次
		"""
		component_info = weixin_models.ComponentInfo.get(app_id=component_info['app_id'])
		data = {
			'appid': appid,
			#'secret': weixin_mp_user_access_token.app_secret,
			'code': code,
			'grant_type': 'authorization_code',
			'component_appid': component_info.app_id,
			'component_access_token': component_info.component_access_token
		}
		url = 'https://api.weixin.qq.com/sns/oauth2/component/access_token'

		try:
			req = urllib2.urlopen(url, urllib.urlencode(data))
			response_data = eval(req.read())
		except:
			try:
				req = urllib2.urlopen(url, urllib.urlencode(data))
				response_data = eval(req.read())
			except:
				notify_message = u"oauth2 access_token: cause:\n{}".format(unicode_full_stack())
				print notify_message
				watchdog_error(notify_message)
		print '>>>>>>>>>>>>>>>>>>>>>response_data:',response_data
		if response_data.has_key('openid'):
			return response_data['openid']
		return 'bill_jobs'

	def raise_response(self, body, headers=None, status=falcon.HTTP_200):
		raise HTTPStatus(status, headers, json.dumps(body))
		