# -*- coding: utf-8 -*-

"""为开放平台账号增加默认账号
"""

__author__ = 'bert'
from util.command import BaseCommand

from business.account.member_factory import MemberFactory
from business.account.webapp_user_factory import WebAppUserFactory
from business.account.webapp_owner import WebAppOwner
from business.account.access_token import AccessToken as BusinessAccessToken

from db.account import models as account_models
from db.member import models as member_models
from eaglet.core.zipkin import zipkin_client
zipkin_client.zipkinClient = None

class Command(BaseCommand):
	help = "python manage.py add_member_for_open [woid]"
	args = ''
	
	def handle(self, woid, **options):
		webapp_owner = WebAppOwner.get({
				'woid': woid
			})

		if not webapp_owner :
			print ("error woid")
			return
		if webapp_owner.mall_type != 1:
			print ("mall type != 1")
			return

		openid = "openid_%s" % woid
		try:
			social_account = member_models.SocialAccount.get(webapp_id=webapp_owner.webapp_id, openid=openid)
		except:
			social_account = None

		if not social_account:
			member = MemberFactory.create({
				"webapp_owner": webapp_owner,
				"openid": openid,
				"for_oauth": 0
				}).save()
		access_token = BusinessAccessToken(woid, openid).put_access_token()
		print ("access_token:%s" % access_token)