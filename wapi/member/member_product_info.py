# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required

import resource


class MemberProductInfo(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'member'
	resource = 'member_product_info'

	@param_required(['woid', 'wuid', 'product_id'])
	def get(args):
		"""
		获取商品详情

		@param id 商品ID
		"""
		return resource.get('member', 'member_product_info', {
			"woid": args['woid'],
			"wuid": args['wuid'],
			"member": None,
			"product_id": args['product_id']
		})