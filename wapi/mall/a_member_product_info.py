# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required

import resource
from db.mall import models as mall_models

class MemberProductInfo(api_resource.ApiResource):
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
		webapp_owner_id = args['webapp_owner'].id
		wuid = args['webapp_user'].id
		member = args['member']

		result_data = dict()
		shopping_cart_count = mall_models.ShoppingCart.select().dj_where(webapp_user_id=wuid).count()
		result_data['count'] = shopping_cart_count
		product_id = args.get('product_id')
		if member:
			member_id = member.id
			if product_id:
				collect = MemberProductWishlist.objects.filter(
					owner_id=webapp_owner_id,
					member_id=member_id,
					product_id=product_id,
					is_collect=True
				)
				if collect.count() > 0:
					result_data['is_collect'] = 'true'
				else:
					result_data['is_collect'] = 'false'
			member_grade_id, discount = member.discount
			result_data['member_grade_id'] = member_grade_id
			result_data['discount'] = discount
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