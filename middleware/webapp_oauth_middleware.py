# -*- coding: utf-8 -*-

from db.account import models as account_models
import resource
from business.account.webapp_owner import WebAppOwner
from business.account.member import Member
from business.account.webapp_user import WebAppUser
from business.account.system_account import SystemAccount
from utils import msg_crypt,auth_util
import settings
import logging

class WebAppOAuthMiddleware(object):
	"""
	获取webapp owner的中间件(填充`webapp_owner`对象)

	@note 优先通过access_token获取 WebAppOwner。开发模式下，优先用`woid`。
	@note 获取access_token时，如果无openid（会员创建时无openid）,使用notopenid 进行授权取得会员openid后重新发起授权
	"""
	def process_request(sel, req, resp):
		if '/user/access_token' in req.path:
			return

		if 'access_token' in req.params:
			if settings.DEBUG:
				print 'WebAppOAuthMiddleware:access_token:>>>>>>>>>>>>>',req.params['access_token']
			access_token = auth_util.decrypt_access_token(req.params['access_token']) 
			access_token_list = access_token.split('_weizoom_')
			if len(access_token_list) != 2:
				raise ValueError('error access_token')
			webapp_owner_id, openid = access_token_list[0], access_token_list[1]

		elif settings.MODE == "develop":
			# 开发测试支持 不传递woid使用jobs用户，不传递openid使用bill_jobs会员
			# if not 'woid' in req.params:
			# 	return
			webapp_owner_id = req.params.get('woid')
			if not webapp_owner_id:
				webapp_owner_id = account_models.User.select().dj_where(username='jobs')[0].id
			openid = req.params.get('openid')
			if not openid:
				openid = 'bill_jobs'
		else:
			raise ValueError("error access_token")

		#TODO2: 支持开发的临时解决方案，需要删除
		#openid = 'bill_jobs'
		#填充webapp_owner
		webapp_owner = WebAppOwner.get({
			'woid': webapp_owner_id
		})
		req.context['webapp_owner'] = webapp_owner
		if openid == 'notopenid':
			return
		#填充会员帐号信息
		system_account = SystemAccount.get({
			'webapp_owner':  webapp_owner,
			'openid': openid
		})
		# member = Member.from_model({
		# 	'webapp_owner': webapp_owner, 
		# 	'model': social_account_info_obj['member']
		# })
		#member.webapp_user = webapp_user
		
		req.context.update({
			'webapp_user': system_account.webapp_user
		})