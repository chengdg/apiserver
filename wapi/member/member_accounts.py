# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required

import resource


class MemberAccounts(api_resource.ApiResource):
	"""
	会员相关账号
	"""
	app = 'member'
	resource = 'member_accounts'

	@param_required(['openid', 'wid'])
	def get(args):
		"""
		获取商品详情

		@param id 商品ID
		"""
		return resource.get('member', 'member_accounts', {
			"openid": args['openid'],
			"wid": args['wid']
		})

	@param_required(['openid', 'wid', 'for_oauth', 'fmt'])
	def post(args):
		"""
		创建会员接口

		@param openid 公众号粉丝唯一标识
		@param wid wid
		@param for_oauth 是否是通过授权获得的openid
		
		"""
		return resource.post('member', 'member_accounts', {
			"openid": args['openid'],
			"wid": args['wid'],
			"for_oauth": args['for_oauth'],
			"fmt": args['fmt']
		})

