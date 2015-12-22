# -*- coding: utf-8 -*-
"""@package business.member.member_factory
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
from hashlib import md5
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
# from cache import utils as cache_util
from db.member import models as member_models
#import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
import settings
from business.decorator import cached_context_property
from business.account.member import Member


class MemberFactory(business_model.Model):
	"""会员成器
	"""
	__slots__ = (
		'id',
		'created',
		'token',
		'webapp_id',
		'integral'
	)

	@staticmethod
	@param_required(['webapp_owner', 'openid', 'for_oauth'])
	def create(args):
		"""工厂方法，创建Member对象

		@return Order对象
		"""
		member_factory = MemberFactory(args['webapp_owner'], args['openid'], args['for_oauth'])

		return member_factory

	def __init__(self, webapp_owner, openid, for_oauth):
		business_model.Model.__init__(self)
		self.context['created'] = True
		self.context['webapp_owner'] = webapp_owner
		self.context['openid'] = openid
		self.context['for_oauth'] = for_oauth

		print dir(webapp_owner)
		member_grades = webapp_owner.member_grades

		default_grade = None
		for grade in member_grades:
			if grade.is_default_grade:
				default_grade = grade
				break
		self.context['default_grade'] = default_grade
		self.context['default_tag'] = webapp_owner.default_member_tag


	def _generate_member_token(self, social_account):
		return "{}{}{}{}".format(
			social_account.webapp_id,
			social_account.platform,
			time.strftime("%Y%m%d"),
			(''.join(random.sample(string.ascii_letters + string.digits, 6))) + str(social_account.id))


	def save(self):
		"""保存会员信息
		"""
		webapp_owner = self.context['webapp_owner']
		member_grade = self.context['default_grade']
		for_oauth = self.context['for_oauth']
		openid = self.context['openid']

		member_business_object = Member.empty_member()
		webapp_id = webapp_owner.webapp_id

		token = md5('%s_%s' % (webapp_id, openid)).hexdigest()
		self.created = True
		sure_created = False		
		try:
			social_account = member_models.SocialAccount.get(webapp_id = webapp_id, openid = openid)
		except:
			social_account, sure_created = member_models.SocialAccount.get_or_create(
				platform = 0,
				webapp_id = webapp_id,
				openid = openid,
				token = token,
				is_for_test = False,
				access_token = '',
				uuid=''
			)
		
		if member_models.MemberHasSocialAccount.select().dj_where(webapp_id=webapp_id, account=social_account).count() >  0:
			self.created = False
			member =  member_models.MemberHasSocialAccount.select().dj_where(webapp_id=webapp_id, account=social_account).first().member
		else:
		#默认等级
			#member_grade = member_models.MemberGrade.get_default_grade(webapp_id)
			if int(for_oauth):
				is_subscribed = False
				status = member_models.NOT_SUBSCRIBED
				is_for_test = False
			else:
				is_subscribed = True
				status = member_models.SUBSCRIBED
				is_for_test = True

			#temporary_token = _create_random()
			member_token = self._generate_member_token(social_account)
			member = member_models.Member.create(
				webapp_id = social_account.webapp_id,
				user_icon = '',#social_account_info.head_img if social_account_info else '',
				username_hexstr = '',
				grade = member_grade,
				remarks_name = '',
				token = member_token,
				is_for_test = is_for_test,
				is_subscribed = is_subscribed,
				status = status
			)
			# if not member:
			# 	return None

			member_models.MemberHasSocialAccount.create(
						member = member,
						account = social_account,
						webapp_id = webapp_id
						)

			member_models.WebAppUser.create(
				token = member.token,
				webapp_id = webapp_id,
				member_id = member.id
				)

			#添加默认分组
			#try:
			default_member_tag = self.context['default_tag']
			if default_member_tag:
				if member_models.MemberHasTag.select().dj_where(member=member, member_tag_id=default_member_tag.id).count() == 0:
					MemberHasTag.create(member=member, member_tag=default_member_tag.id)

			
			member_models.MemberInfo.create(
				member=member,
				name='',
				weibo_nickname=''
				)
		member_business_object.id = member.id
		member_business_object.created = self.created
		member_business_object.token = member.token
		member_business_object.webapp_id = member.webapp_id

		return member_business_object
