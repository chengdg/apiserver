# -*- coding: utf-8 -*-

from urllib import quote
from core import api_resource
from core.cache import utils as cache_util

from wapi.decorators import param_required
from utils import auth_util

from db.account.models import User
from utils import error_codes
from business.account.access_token import AccessToken as BusinessAccessToken
from business.account.webapp_owner import WebAppOwner
from business.account.system_account import SystemAccount
from business.account.member_factory import MemberFactory

import settings

class AccessToken(api_resource.ApiResource):
	"""
	access_token
	"""
	app = 'user'
	resource = 'access_token'

	@param_required(['woid', 'openid'])
	def put(args):
		"""
		获取access_token
		"""
		woid = args['woid']
		openid = args['openid']


		#验证woid
		webapp_owner = WebAppOwner.get({
			'woid': woid
		})
		if not webapp_owner:		
			return {"errorcode": error_codes.ILLEGAL_WOID_CODE, "errmsg": error_codes.code2msg[error_codes.ILLEGAL_WOID_CODE]}
			
		#填充会员帐号信息
		#进入授权的帐号信息都是已存在的
		try:
			system_account = SystemAccount.get({
				'webapp_owner':  webapp_owner,
				'openid': openid
			})
		except:
			if settings.MODE == 'develop':
				#创建会员
				member = MemberFactory.create({
					"webapp_owner": webapp_owner,
					"openid": openid,
					"for_oauth": 0
					}).save()
				system_account = SystemAccount.get({
					'webapp_owner':  webapp_owner,
					'openid': openid
				})
			else:
				system_account = None

		if not system_account:
			return {"errorcode": error_codes.ILLEGAL_OPENID_CODE, "errmsg": error_codes.code2msg[error_codes.ILLEGAL_OPENID_CODE]}
		
		#加密access_token
		access_token = BusinessAccessToken(woid, openid).get_access_token()

		if not access_token:
			access_token = BusinessAccessToken(woid, openid).get_access_token()

		if not access_token:
			return {"errorcode": error_codes.SYSTEM_ERROR_CODE, "errmsg": error_codes.code2msg[error_codes.SYSTEM_ERROR_CODE]}

		data = {
			"access_token": access_token
		}

		return data


	@param_required(['access_token'])
	def get_sys_account(args):
		access_token = args['access_token']
		value = BusinessAccessToken.get({
			'access_token': access_token
			})

		if not value:
			return {"errorcode": error_codes.ILLEGAL_ACCESS_TOKEN_CODE, "errmsg": error_codes.code2msg[error_codes.ILLEGAL_ACCESS_TOKEN_CODE]}
		else:			
			webapp_owner = WebAppOwner.get({
				'woid': value.woid
			})

			system_account = SystemAccount.get({
				'webapp_owner':  webapp_owner,
				'openid': value.openid
			})

			return {"webapp_owner": webapp_owner, "system_account": system_account}
