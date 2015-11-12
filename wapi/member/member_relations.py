# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required

import resource


class MemberRelations(api_resource.ApiResource):
	"""
	会员相关账号
	"""
	app = 'member'
	resource = 'member_relations'

	@param_required(['member_id'])
	def get(args):
		"""
		获取好友ids

		@param member_id 会员ID
		"""
		return resource.get('member', 'member_relations', {
			"member_id": args['member_id']
			#"wid": args['wid']
		})

	@param_required(['mt', 'fmt', 'is_fans', 'r_url'])
	def post(args):
		"""
		创建会员关系

		@param mt 当前会员toke
		@param fmt 分享会员token
		@param is_fans 是否是fans
		@param r_url 当前url路径
		
		"""
		return resource.post('member', 'member_relations', {
			"mt": args['mt'],
			"fmt": args['fmt'],
			"is_fans": args['is_fans'],
			"r_url": args['r_url']
		})

