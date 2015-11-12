# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required

import resource


class MemberShareUrl(api_resource.ApiResource):
	"""
	会员相关账号
	"""
	app = 'member'
	resource = 'member_share_url'

	# @param_required(['member_id'])
	# def get(args):
	# 	"""
	# 	获取好友ids

	# 	@param member_id 会员ID
	# 	"""
	# 	return resource.get('member', 'member_relations', {
	# 		"member_id": args['member_id']
	# 		#"wid": args['wid']
	#})

	@param_required(['r_url', 'umt', 'cmt', 'order_id'])
	def post(args):
		"""
		处理分享链接

		@param r_url 访问路径
		@param umt 分享者token
		@param cmt 当前点击会员token
		@param order_id 引导购买订单id
		
		"""
		return resource.post('member', 'member_share_url', {
			"umt": args['umt'],
			"cmt": args['cmt'],
			"order_id": args['order_id'],
			"r_url": args['r_url']
		})

