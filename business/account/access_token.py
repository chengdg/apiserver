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
from db.account import models as account_models

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

		try:
			db_model = account_models.AccessToken.get(access_token=access_token)
			return AccessToken(db_model.woid, db_model.openid, access_token)
		except :
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
		try:
			db_model = account_models.AccessToken.get(woid=self.woid, openid=self.openid)
		except:
			db_model = None
		if db_model:
			self.access_token = db_model.access_token
			return self.access_token
		else:
			access_token = auth_util.encrypt_access_token(self.woid, self.openid)
			
			self.access_token = access_token

			try:
				db_model = account_models.AccessToken(
					woid=self.woid, 
					openid=self.openid, 
					times=str(int(time.time())),
					access_token=access_token,
					expires_in='100000000000'
					).save()
				return access_token
			except:
				try:
					db_model = account_models.AccessToken(
						woid=self.woid, 
						openid=self.openid, 
						times=str(int(time.time())),
						access_token=access_token,
						expires_in='1000000000000'
						).save()
					return access_token
				except:
					notify_message = u"AccessToken get_access_token cause:\n{}".format(unicode_full_stack())
					logging.error(notify_message)
					watchdog_error(notify_message)
					return None
