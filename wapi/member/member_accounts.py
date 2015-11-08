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