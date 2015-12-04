# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required

import resource
from db.mall import models as mall_models
from business.mall.shopping_cart import ShoppingCart

class AMemberProductInfo(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'member_product_info'

	@param_required([])
	def get(args):
		"""
		获取商品详情

		@param id 商品ID
		"""
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		product_id = args.get('product_id', None)

		result_data = dict()

		result_data['count'] = webapp_user.shopping_cart.product_count

		member = webapp_user.member
		if member:
			if product_id:
				result_data['is_collect'] = webapp_user.is_collect_product(product_id)
			result_data['member_grade_id'] = member.id
			result_data['discount'] = member.discount
			result_data['usable_integral'] = member.integral
			result_data['is_subscribed'] = member.is_subscribed
		else:
			if product_id:
				result_data['is_collect'] = 'false'
			result_data['member_grade_id'] = -1
			result_data['discount'] = 100
			result_data['usable_integral'] = 0
			result_data['is_subscribed'] = False

		return result_data