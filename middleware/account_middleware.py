# -*- coding: utf-8 -*-

from db.account import models as account_models
import resource
from business.account.webapp_owner import WebAppOwner
from business.account.member import Member
from business.account.webapp_user import WebAppUser
from business.account.social_account_info import SocialAccountInfo

class WebAppOwnerMiddleware(object):
	"""
	获取webapp owner的中间件
	"""
	def process_request(sel, req, resp):
		if not 'woid' in req.params:
			return

		webapp_owner_id = req.params['woid']
		webapp_owner = WebAppOwner.get({
			'woid': webapp_owner_id
		})
		req.context['webapp_owner'] = webapp_owner


class AccountsMiddleware(object):
	def process_request(sel, req, resp):
		if not 'webapp_owner' in req.context:
			return

		openid = req.params.get('oauth', 'bill_jobs')
		if openid:
			social_account_info_obj = SocialAccountInfo.get({
				'webapp_owner':  req.context['webapp_owner'],
				'openid': openid
				})

			req.context.update(social_account_info_obj.to_dict())
		else:
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
			member.webapp_user = webapp_user
			member_accounts['member'] = member
			member_accounts['webapp_user'] = webapp_user
			req.context.update(member_accounts)

