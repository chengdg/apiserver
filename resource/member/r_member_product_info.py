# -*- coding: utf-8 -*-

import json

from bs4 import BeautifulSoup

from core import resource
from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
import settings

class RMemberProductInfo(resource.Resource):
	"""
	商品详情
	"""
	app = 'member'
	resource = 'member_product_info'

	@param_required(['woid', 'wuid', 'member', 'product_id'])
	def get(args):
		woid = args['woid']
		wuid = args['wuid']
		member = args['member']

		result_data = dict()
		shopping_cart_count = mall_models.ShoppingCart.select().dj_where(webapp_user_id=wuid).count()
		result_data['count'] = shopping_cart_count
		webapp_owner_id = args['woid']
		product_id = args['product_id']
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
			member_grade_id, discount = get_member_discount(request)
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
