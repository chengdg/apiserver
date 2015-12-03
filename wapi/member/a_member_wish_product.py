# -*- coding: utf-8 -*-
import json

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from utils import dateutil as utils_dateutil
import resource
from business.mall.product import Product


class AMemberWishProduct(api_resource.ApiResource):
	"""
	会员收藏商品
	"""
	app = 'member'
	resource = 'wish_product'

	@param_required(['webapp_user', 'product_id'])
	def put(args):
		webapp_user = args['webapp_user']
		product_id = args['product_id']
		member = webapp_user.member
		member.collect_product(product_id)
		return {}

	@param_required(['webapp_user', 'product_id', 'wished'])
	def post(args):
		webapp_user = args['webapp_user']
		product_id = args['product_id']
		wished = args['wished']
		member = webapp_user.member
		if str(wished) == '1':
			member.collect_product(product_id)
		else:
			member.cancel_collect_product(product_id)
		return {}



