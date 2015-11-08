# -*- coding: utf-8 -*-

from wapi.user import models as account_models
import resource


class WebAppOwnerUserProfileMiddleware(object):
	"""
	获取webapp owner的user profile
	"""
	def process_request(sel, req, resp):
		if not 'woid' in req.params:
			return

		webapp_owner_id = req.params['woid']
		webapp_owner_profile = account_models.UserProfile.get(user=webapp_owner_id)
		req.context['webapp_owner_profile'] = webapp_owner_profile


class AccountsMiddleware(object):
	def process_request(sel, req, resp):
		if not 'webapp_owner_profile' in req.context:
			return

		openid = 'bill_jobs'
		webapp_id = req.context['webapp_owner_profile'].webapp_id
		member_accounts = resource.get('member', 'member_accounts', {
			"openid": openid,
			"wid": webapp_id,
			"return_model": True
		})
		req.context.update(member_accounts)
