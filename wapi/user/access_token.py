# -*- coding: utf-8 -*-

from urllib import quote
from core import api_resource
from wapi.decorators import param_required
from utils import auth_util

from db.account.models import User
from utils import error_codes

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
		try:
			user = User.get(id=woid)
		except:
			return {"errorcode": error_codes.ILLEGAL_WOID_CODE, "errmsg": error_codes.code2msg[error_codes.ILLEGAL_WOID_CODE]}
			
			
		"""
			TODO:
				1、openid是有效
		"""
		if not openid:
			return {"errorcode": error_codes.ILLEGAL_OPENID_CODE, "errmsg": error_codes.code2msg[error_codes.ILLEGAL_OPENID_CODE]}
		
		access_token = auth_util.encrypt_access_token(str(woid), openid)
		data = {
			"access_token": quote(access_token), "expires_in": "100000000"
		}

		"""
			TODO:
				1.创建或者获取会员信息
				2.存储ac信息和对应会员信息 key-value
		"""


		return data

