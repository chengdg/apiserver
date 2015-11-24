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
from wapi import wapi_utils
from db.member import models as member_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
import settings
from business.decorator import cached_context_property

class MemberSharedUrlFactory(business_model.Model):
	"""会员分享链接生成器
	"""
	__slots__ = (
		'member_id',
		'url',
		'shared_url_digest',
		'followed'
	)

	@staticmethod
	@param_required(['member_id', 'url', 'shared_url_digest', 'followed'])
	def create(args):
		"""工厂方法，创建MemberSharedUrlFactory对象

		@return MemberFollowRelaton对象
		"""
		member_factory = MemberSharedUrlFactory(args['member_id'], args['url'], args['shared_url_digest'], args['followed'])

		return member_factory

	def __init__(self, member_id, url, shared_url_digest, followed):
		business_model.Model.__init__(self)
		self.member_id = member_id
		self.url = url
		self.shared_url_digest = shared_url_digest
		self.followed = followed
		print '>>>>>>>>>>>>>>>>>>>>>>>>123,',followed

	def save(self):
		"""创建分享链接
		"""
		if self.followed:
			member_models.MemberSharedUrlInfo.create(
						member = self.member_id,
						shared_url = self.url,
						shared_url_digest = self.shared_url_digest,
						pv = 1,
						leadto_buy_count = 0,
						followers = 1
						)
		else:
			member_models.MemberSharedUrlInfo.create(
						member = self.member_id,
						shared_url = self.url,
						shared_url_digest = self.shared_url_digest,
						pv = 1,
						leadto_buy_count = 0,
						followers = 0
						)

	def update(self):
		"""更新分享链接
		"""
		if not self.followed:
			update = member_models.MemberSharedUrlInfo.update(pv=member_models.MemberSharedUrlInfo.pv+1).dj_where(member_id=self.member_id,shared_url_digest=self.shared_url_digest)
		else:
			update = member_models.MemberSharedUrlInfo.update(pv=member_models.MemberSharedUrlInfo.pv+1, followers=member_models.MemberSharedUrlInfo.followers+1).dj_where(member_id=self.member_id,shared_url_digest=self.shared_url_digest)
		update.execute()



