# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
#from api.wapi_utils import create_json_response
from business.account.member_factory import MemberFactory
from business.account.webapp_user_factory import WebAppUserFactory
from business.account.webapp_owner import WebAppOwner
from business.account.access_token import AccessToken as BusinessAccessToken

from db.account import models as account_models
from db.member import models as member_models

class Token(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'user'
	resource = 'token'

	@param_required(['woid'])
	def put(args):
		"""
		创建商品
		"""
		woid = args["woid"]
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
		return {
			"access_token": access_token
		}
