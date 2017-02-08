# -*- coding: utf-8 -*-

__author__ = 'robert'

from datetime import datetime
import array
import json

from bson import json_util

from util.command import BaseCommand
from eaglet.core.cache import utils as cache_util
from db.account.models import User, UserProfile
from db.member import models as member_models

class Command(BaseCommand):
	help = "delete member [mp user] [weixin user]"
	args = ''
	
	def handle(self, mp_user_name, weixin_user_name, **options):
		mp_user = User.get(username=mp_user_name)
		mp_user_profile = UserProfile.get(user=mp_user.id)

		member = member_models.Member.get(webapp_id=mp_user_profile.webapp_id, username_hexstr=weixin_user_name)

		openid = '%s_%s' % (weixin_user_name, mp_user_name)
		social_account = member_models.SocialAccount.get(webapp_id=mp_user_profile.webapp_id, openid=openid)

		member_models.MemberHasSocialAccount.delete().dj_where(member=member.id, webapp_id=mp_user_profile.webapp_id).execute()
		print 'delete <member, social_account>'

		member_models.MemberInfo.delete().dj_where(member_id=member.id).execute()
		print 'delete member info'

		member_models.WebAppUser.delete().dj_where(member_id=member.id, webapp_id=mp_user_profile.webapp_id).execute()
		print 'delete webapp user'

		member_models.Member.delete().dj_where(id=member.id).execute()
		print 'delete member'

		member_models.SocialAccount.delete().dj_where(id=social_account.id).execute()
		print 'delete social account'

		print '[success]'
