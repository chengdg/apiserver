# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup
from datetime import datetime

from core import inner_resource
from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
from wapi.member import models as member_models
import settings

class RMemberAccounts(inner_resource.Resource):
	"""
	与会员相关的账号，包括member, social_account, weapp_user
	"""
	app = 'member'
	resource = 'member_accounts'

	@staticmethod
	def get_accounts_for_cache(openid, webapp_id):
		def inner_func():
			social_account = member_models.SocialAccount.get(webapp_id=webapp_id, openid=openid)
			member = member_models.Member.get(id=member_models.MemberHasSocialAccount.select().dj_where(account=social_account)[0].member.id)
			if member_models.WebAppUser.select().dj_where(webapp_id=webapp_id, member_id=member.id, father_id=0).count() == 0:
				webapp_user = member_models.WebAppUser.select().dj_where(webapp_id=webapp_id, member_id=member.id, father_id=0, token=member.id)
			else:
				webapp_user = member_models.WebAppUser.select().dj_where(webapp_id=webapp_id, member_id=member.id, father_id=0)[0]
			today = datetime.today()
			date_str = datetime.today().strftime('%Y-%m-%d') 
			return {
				'value': {
					'member': member.to_dict(),
					'webapp_user': webapp_user.to_dict(),
					'social_account': social_account.to_dict(),
					'date_time':date_str
				}
			}

		return inner_func

	@param_required(['openid', 'wid'])
	def get(args):
		openid = args['openid']
		webapp_id = args['wid']

		today = datetime.today()
		date_str = datetime.today().strftime('%Y-%m-%d') 
		key = 'member_{webapp:%s}_{openid:%s}' % (webapp_id, openid)
		data = cache_util.get_from_cache(key, RMemberAccounts.get_accounts_for_cache(openid, webapp_id))
		if data['date_time'] != date_str:
			cache_util.delete_pattern(key)
			data = cache_util.get_from_cache(key, get_accounts_for_cache(openid, webapp_id))

		if 'return_model' in args:
			member = member_models.Member.from_dict(data['member'])
			webapp_user = member_models.WebAppUser.from_dict(data['webapp_user'])
			social_account = member_models.SocialAccount.from_dict(data['social_account'])
			member.webapp_user = webapp_user
			webapp_user.member = member
			return {
				'member': member,
				'webapp_user': webapp_user,
				'social_account': social_account
			}
		else:
			return data
