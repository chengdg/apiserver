# -*- coding: utf-8 -*-
import json

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from utils import dateutil as utils_dateutil
import resource
from business.mall.product import Product


class AMemberCollectedProduct(api_resource.ApiResource):
	"""
	会员收藏商品
	"""
	app = 'member'
	resource = 'collected_product'

	@param_required(['webapp_user', 'product_id'])
	def put(args):
		webapp_user = args['webapp_user']
		product_id = args['product_id']
		webapp_user.collected_product(product_id)
		return {}

	@param_required(['webapp_user', 'product_id'])
	def delete(args):
		webapp_user = args['webapp_user']
		product_id = args['product_id']
		webapp_user.cancel_collected_product(product_id)
		return {}



