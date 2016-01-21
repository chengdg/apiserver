# -*- coding: utf-8 -*-

from db.account import models as account_models
#import resource
from business.account.webapp_owner import WebAppOwner
#from business.account.member import Member
#from business.account.webapp_user import WebAppUser
from business.account.system_account import SystemAccount
#from services.record_member_pv_service.task import record_member_pv
from wapi.user.access_token import AccessToken
#from utils import msg_crypt,auth_util
import settings
import logging

from core.redirects import HTTPMiddlewareError

class WebAppAccountMiddleware(object):
	"""
	获取webapp owner的中间件(填充`webapp_owner`对象)

	@note 优先通过access_token获取 WebAppOwner。开发模式下，优先用`woid`。
	@note 获取access_token时，如果无openid（会员创建时无openid）,使用notopenid 进行授权取得会员openid后重新发起授权
	"""
	def process_request(sel, req, resp):
		if '/user/access_token' in req.path or '/console/' in req.path:
			logging.info("skipped in WebAppAccountMiddleware. req.path: {}".format(req.path))
			return

		if 'access_token' in req.params:
			access_token = req.params.get('access_token', None)	
			account_info = AccessToken.get_sys_account({
				'access_token':access_token
				})
			if settings.DEBUG:
				logging.debug( 'WebAppOAuthMiddleware:access_token:>>>>>>>>>>>>>%s' % req.params['access_token'])
				logging.debug( 'account_info from access_token>>>>>>>>>>>>:%s' % account_info)

			if account_info.has_key('errorcode'):
				raise HTTPMiddlewareError(account_info)
	
			woid = account_info['webapp_owner'].id
			req.context['webapp_owner'] = account_info['webapp_owner']
			req.context['webapp_user'] = account_info['system_account'].webapp_user
			return 

		elif settings.MODE == "develop" or settings.MODE == "test":
			# 开发测试支持 不传递woid使用jobs用户，不传递openid使用bill_jobs会员
			# if not 'woid' in req.params:
			# 	return
			woid = req.params.get('woid')
			if not woid:
				woid = account_models.User.select().dj_where(username='jobs')[0].id
			openid = req.params.get('openid')
			if not openid:
				openid = 'bill_jobs'
		else:
			raise ValueError("error access_token")

		if req.context.has_key('webapp_owner') and req.context.has_key('webapp_user'):
			return
		#TODO2: 支持开发的临时解决方案，需要删除
		print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.1111'
		openid = 'bill_jobs'
		#填充webapp_owner
		webapp_owner = WebAppOwner.get({
			'woid': woid
		})
		req.context['webapp_owner'] = webapp_owner
		
		print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.222222',openid
		if openid == 'notopenid':
			return
		#填充会员帐号信息
		system_account = SystemAccount.get({
			'webapp_owner':  webapp_owner,
			'openid': openid
		})
		print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.3333',system_account
		req.context.update({
			'webapp_user': system_account.webapp_user
		})
