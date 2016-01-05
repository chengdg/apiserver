# -*- coding: utf-8 -*-
"""@package business.account.member_info_updater
会员信息定时更新器

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from db.member import models as member_models
from business import model as business_model
from business.decorator import cached_context_property
from business.account.webapp_user import WebAppUser
from utils import emojicons_util
from utils.string_util import hex_to_byte, byte_to_hex

from core.wxapi import get_weixin_api
from core.cache import utils as cache_util
from core.watchdog.utils import watchdog_alert

import settings

class MemberInfoUpdater(business_model.Model):
	"""会员信息定时更新器
	"""
	__slots__ = ()

	def __init__(self, webapp_owner):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner

	def update(self, webapp_user_id):
		"""更新会员信息

		每天更新一次，处理以下情况：
			1. 会员更改昵称
			2. 会员取消关注
		"""
		print 'TODO2: update member info'

		webapp_user = WebAppUser.from_id({
			'webapp_owner': self.context['webapp_owner'],
			'id': webapp_user_id
			})
		webapp_owner = self.context['webapp_owner']
		mpuser_access_token = webapp_owner.weixin_mp_user_access_token
		weixin_api = get_weixin_api(mpuser_access_token)
		userinfo = weixin_api.get_user_info(webapp_user.openid)


		if not userinfo:
			member = webapp_user.member
			if hasattr(userinfo, 'nickname'):
				nickname = userinfo.nickname
				if isinstance(nickname, unicode):
					member_nickname_str = nickname.encode('utf-8')
				else:
					member_nickname_str = nickname

				username_hexstr = byte_to_hex(member_nickname_str)
			else:
				username_hexstr = ''
		
			if hasattr(userinfo, 'headimgurl'):
				headimgurl = userinfo.headimgurl
			else:
				headimgurl = ''
	
			if hasattr(userinfo, 'sex'):
				sex = userinfo.sex
			else:
				sex = 0
	
			if hasattr(userinfo, 'subscribe'):
				if str(userinfo.subscribe) == '1':
					subscribe = True
				else:
					subscribe = False
			else:
				subscribe = False

			if hasattr(userinfo, 'city'):
				city = userinfo.city
			else:
				city = ''
			
			if hasattr(userinfo, 'province'):
				province = userinfo.province
			else:
				province = ''
			
			if hasattr(userinfo, 'country'):
				country = userinfo.country
			else:
				country = ''

			if subscribe is False:
				if member.is_subscribed:
					status = 0
				else:
					status = member.status
				member_models.Member.update(is_subscribed=False, status=status).dj_where(id=member.id)
			else:
				member_models.Member.update(
					is_subscribed=True, 
					update_time=datetime.now(),
					username_hexstr=username_hexstr,
					city=city,
					province=province,
					country=country,
					sex=sex,
					status=1).dj_where(id=member.id)

			webapp_user.cleanup_cache()