# -*- coding: utf-8 -*-
"""@package business.spread.MemberRelatonFactory
订单生成器

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
#import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
import settings
from business.decorator import cached_context_property

class MemberRelatonFactory(business_model.Model):
	"""会员关系成器
	"""
	__slots__ = (
		'member_id',
		'follower_member_id',
		'is_fans'
	)

	@staticmethod
	@param_required(['member_id', 'follower_member_id', 'is_fans'])
	def create(args):
		"""工厂方法，创建MemberRelatonFactory对象

		@return MemberFollowRelaton对象
		"""
		member_factory = MemberRelatonFactory(args['member_id'], args['follower_member_id'], args['is_fans'])

		return member_factory

	def __init__(self, member_id, follower_member_id, is_fans):
		business_model.Model.__init__(self)
		self.member_id = member_id
		self.follower_member_id = follower_member_id
		self.is_fans = is_fans

	def save(self):
		"""保存关系
		"""
		if self.member_id and self.follower_member_id and self.member_id != self.follower_member_id:
			member_models.MemberFollowRelation.create(member_id=self.member_id, follower_member_id=self.follower_member_id, is_fans=self.is_fans)
			member_models.MemberFollowRelation.create(member_id=self.follower_member_id, follower_member_id=self.member_id, is_fans=False)