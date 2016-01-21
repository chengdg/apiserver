# -*- coding: utf-8 -*-
"""@package business.spread

"""

import json
from bs4 import BeautifulSoup
import math
import itertools
import uuid
import time
import random
import string

from wapi.decorators import param_required
#from wapi import wapi_utils
from db.member import models as member_models
#import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
import settings
from business.decorator import cached_context_property

class MemberClickedFactory(business_model.Model):
	"""会员分享链接生成器
	"""
	__slots__ = (
		'url_member_id',
		'click_member_id',
		'url',
		'shared_url_digest'
	)

	@staticmethod
	@param_required(['url_member_id', 'click_member_id','url', 'shared_url_digest'])
	def create(args):
		"""工厂方法，创建MMemberClickedFactory对象

		@return MemberClickedFactory对象
		"""
		member_clicked_factory = MemberClickedFactory(args['url_member_id'], args['click_member_id'], args['url'], args['shared_url_digest'])

		return member_clicked_factory

	def __init__(self, url_member_id, click_member_id, url, shared_url_digest):
		print 'click_member_id>>>>>>>>>>>>>>>>>>>>>>>',click_member_id
		business_model.Model.__init__(self)
		self.url_member_id = url_member_id
		self.click_member_id = click_member_id
		self.url = url
		self.shared_url_digest = shared_url_digest

	def save(self):
		"""创建会员点击记录
		"""
		member_models.MemberClickedUrl.create(
				url = self.url,
				url_digest = self.shared_url_digest,
				mid = self.click_member_id,
				followed_mid = self.url_member_id
				)
		


