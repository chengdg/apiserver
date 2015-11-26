# -*- coding: utf-8 -*-

from db.account import models as account_models
import resource
from business.account.webapp_owner import WebAppOwner
from business.account.member import Member
from business.account.webapp_user import WebAppUser
from business.account.social_account_info import SocialAccountInfo
from utils import msg_crypt,auth_util
import settings

class WebAppOAuthMiddleware(object):
	"""
	获取webapp owner的中间件
	"""
	def process_request(sel, req, resp):
		if 'access_token' in req.params:
			access_token = auth_util.decrypt_access_token(req.params['access_token']) 
			#access_token = '3_weizoom_jobs_test'
			access_token_list = access_token.split('_weizoom_')
			if len(access_token_list) != 2:
				raise 'error access_token' 
			webapp_owner_id, openid = access_token_list[0], access_token_list[1]
			#填充webapp_owner
			webapp_owner = WebAppOwner.get({
				'woid': webapp_owner_id
			})
			req.context['webapp_owner'] = webapp_owner
			if openid == 'notopenid':
				return
			#填充会员帐号信息
			social_account_info_obj = SocialAccountInfo.get({
				'webapp_owner':  webapp_owner,
				'openid': openid
				}).to_dict()
			webapp_user = social_account_info_obj['webapp_user']
			member = social_account_info_obj['member']
			# member = Member.from_model({
			# 	'webapp_owner': webapp_owner, 
			# 	'model': social_account_info_obj['member']
			# })
			#member.webapp_user = webapp_user
			webapp_user.member = member
			social_account_info_obj['member'] = member
			social_account_info_obj['webapp_user'] = webapp_user
			req.context.update(social_account_info_obj)

		elif settings.MODE == "develop":
			if not 'woid' in req.params:
				return
			webapp_owner_id = req.params['woid']
			webapp_owner = WebAppOwner.get({
				'woid': webapp_owner_id
			})
			req.context['webapp_owner'] = webapp_owner
			openid = 'bill_jobs'
			webapp_id = req.context['webapp_owner'].webapp_id
			member_accounts = resource.get('member', 'member_accounts', {
				"openid": openid,
				"wid": webapp_id,
				"return_model": True
			})
			print 'get member in AccountsMiddleware...'
			member = Member.from_model({
				'webapp_owner': req.context['webapp_owner'], 
				'model': member_accounts['member']
			})
			webapp_user = WebAppUser.from_model({
				'webapp_owner': req.context['webapp_owner'],
				'model': member_accounts['webapp_user']
			})
			webapp_user.member = member
			#member.webapp_user = webapp_user
			#member_accounts['member'] = member
			member_accounts['webapp_user'] = webapp_user
			req.context.update(member_accounts) 
		else:
			raise "error access_token"
