# -*- coding: utf-8 -*-

from business.account.webapp_owner import WebAppOwner as WebAppOwner
from db.account import models as account_models


def get_nickname_from_webapp_id(cache_key, webapp_id):
	"从webapp_id获公众号的nickname，如微众商城，微众妈妈等"
	def inner_func():
		user_id = account_models.UserProfile.select().dj_where(webapp_id=webapp_id).first().user_id
		webapp_owner = WebAppOwner.get({
			'woid': user_id
		})
		nickname = webapp_owner.mp_nick_name
		ret = {
				'keys': [cache_key],
				'value': nickname
			}
		return ret
	return inner_func