# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required

import resource


class MemberCoupons(api_resource.ApiResource):
	"""
	会员优惠券
	"""
	app = 'member'
	resource = 'member_coupons'

	@param_required(['openid', 'woid', 'member'])
	def get(args):
		"""
		获取商品详情

		@param id 商品ID
		"""
		member = args['member']
		return resource.get('member', 'member_coupons', {
			"member": args['member']
		})