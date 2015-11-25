# -*- coding: utf-8 -*-
"""@package business.account.social_account_info
业务层内部使用的业务对象，social account的信息，主要与redis缓存中的会员相关数据对应

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from db.account import models as account_models
import resource
from db.mall import models as mall_models
from db.mall import promotion_models
from db.account import models as account_models
from db.account import weixin_models as weixin_user_models
from db.account import webapp_models as webapp_models
from db.member import models as member_models
import settings
from core.watchdog.utils import watchdog_alert, watchdog_warning, watchdog_error
from core.exceptionutil import unicode_full_stack
from business import model as business_model



class SocialAccountInfo(business_model.Model):
	"""
	social account的信息
	"""
	__slots__ = (
		'member',
		'webapp_user',
		'social_account',
		'date_time'
	)

	@staticmethod
	@param_required(['openid'])
	def get(args):
		"""工厂方法

		@param[in] webapp_owner
		@param[in] openid

		@return WebAppOwnerInfo对象
		"""
		social_account_info = SocialAccountInfo(args['webapp_owner'], args['openid'])
		return social_account_info

	def __init__(self, webapp_owner, openid):
		business_model.Model.__init__(self)
		obj = self.__get_from_cache(webapp_owner.webapp_id, openid)
		for slot in self.__slots__:
			setattr(self, slot, getattr(obj, slot, None))

	def __get_accounts_for_cache(self, openid, webapp_id):
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

	def __get_from_cache(self, webapp_id, openid):
		"""
		social_account cache
		"""
		key = 'social_{webapp:%s}_{openid:%s}' % (webapp_id, openid)

		data = cache_util.get_from_cache(key, self.__get_accounts_for_cache(openid, webapp_id))

		today = datetime.today()
		date_str = datetime.today().strftime('%Y-%m-%d') 
		if data['date_time'] != date_str:
			cache_util.delete_pattern(key)
			data = cache_util.get_from_cache(key, SocialAccountInfo.get_accounts_for_cache(openid, webapp_id))

		obj = cache_util.Object()
		obj.member = member_models.Member.from_dict(data['member'])
		obj.social_account = member_models.SocialAccount.from_dict(data['social_account'])
		obj.webapp_user = member_models.WebAppUser.from_dict(data['webapp_user'])
		return obj





