# -*- coding: utf-8 -*-

__author__ = 'robert'

from datetime import datetime
import array
import json

from bson import json_util
import redis

from util.command import BaseCommand
from eaglet.core.cache import utils as cache_util
from db.account.models import User, UserProfile
from db.member import models as member_models

class Command(BaseCommand):
	help = "create member [mp user] [weixin user]"
	args = ''
	
	def handle(self, mp_user_name, weixin_user_name, **options):
		import settings
		r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=5) #5 is db used by member service
		r.flushdb()
		print "flush member_service's redis cache"

		mp_user = User.get(username=mp_user_name)
		mp_user_profile = UserProfile.get(user=mp_user.id)

		member_grade = member_models.MemberGrade.get(webapp_id=mp_user_profile.webapp_id, is_default_grade=True)

		if member_models.Member.select().dj_where(webapp_id=mp_user_profile.webapp_id, username_hexstr=weixin_user_name).count() > 0:
			print 'member [%s] already exists' % weixin_user_name
			return

		#create new member
		social_account = member_models.SocialAccount.create(
			webapp_id = mp_user_profile.webapp_id,
			token = 'sa_%s_token' % weixin_user_name,
			access_token = 'sa_%s_access_token' % weixin_user_name,
			openid = '%s_%s' % (weixin_user_name, mp_user_name)
		)
		print 'create social account'

		member = member_models.Member.create(
			webapp_id = mp_user_profile.webapp_id,
			token = 'm_%s_token' % weixin_user_name,
			grade = member_grade.id,
			integral = 0,
			is_subscribed = True,
			username_hexstr = weixin_user_name,
			user_icon = ''
		)
		print 'create member'

		member_models.WebAppUser.create(
			token = 'wu_%s_token' % weixin_user_name,
			webapp_id = mp_user_profile.webapp_id,
			member_id = member.id
		)
		print 'create webapp user'

		member_models.MemberInfo.create(
			member = member.id,
			name = weixin_user_name,
			weibo_nickname = '',
			binding_time = datetime.now()
		)
		print 'create member info'

		member_models.MemberHasSocialAccount.create(
			member = member.id,
			account = social_account.id,
			webapp_id = mp_user_profile.webapp_id
		)
		print 'connect <member, social_account>'
		print '[success]'
		


