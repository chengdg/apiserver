# -*- coding: utf-8 -*-
"""@package business.account.access_token
业务层内部使用的业务对象，access_token的信息，主要与redis缓存中的帐号数据对应

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime
import time
import urllib

from wapi.decorators import param_required
from core.cache import utils as cache_util
import settings
from core.watchdog.utils import watchdog_alert, watchdog_warning, watchdog_error
from core.exceptionutil import unicode_full_stack
from business import model as business_model
from utils import auth_util
import logging

class AccessToken(business_model.Model):
	"""
	access_token信息
	"""
	__slots__ = (
		'woid',
		'openid',
		'access_token'
	)

	@staticmethod
	@param_required(['access_token'])
	def get(args):
		"""工厂方法

		@param[in] access_token
		@return AccessToken对象
		"""
		access_token_obj = AccessToken.get_from_cache(args)
		return access_token_obj

	@staticmethod
	@param_required(['access_token'])
	def get_from_cache(args):
		access_token = args['access_token']
		if access_token.find('=') > -1 or access_token.find('+') > -1 or access_token.find('@') > -1:
			access_token = urllib.quote(access_token)
		value = cache_util.GET_CACHE(access_token)
		if value:
			woid = value['woid']
			openid = value['openid']
			#TODO-bert 校验access_token时间有效性
			return AccessToken(woid, openid, access_token)
		else:
			return None

	def __init__(self, woid, openid, access_token=None):
		business_model.Model.__init__(self)
		self.woid = str(woid)
		self.openid = openid
		self.access_token = access_token
	
	def get_access_token(self):
		"""
			get_access_token
		"""
		if self.access_token:
			return self.access_token

		access_token = auth_util.encrypt_access_token(self.woid, self.openid)
		key = access_token
		today = datetime.today()
		date_str = datetime.today().strftime('%Y-%m-%d') 
		value = {
			'woid': self.woid,
			'openid': self.openid,
			'date_str': date_str,
			'expires_in': '100000000000',
			'times': int(time.time())
		}
		self.access_token = key
		#TODU-bert 修改缓存库不使用公共库
		try:
			cache_util.SET_CACHE(key, value)
			return key
		except:
			try:
				cache_util.SET_CACHE(key, value)
				return key
			except:
				notify_message = u"AccessToken get_access_token cause:\n{}".format(unicode_full_stack())
				logging.error(notify_message)
				watchdog_error(notify_message)
				return None
			
		
