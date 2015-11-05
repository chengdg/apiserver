# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
from wapi.mall import models as mall_models
from utils import dateutil as utils_dateutil

import resource


class ProductDetail(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'product_detail'


	@param_required(['product_id'])
	def get(args):
		"""
		获取商品详情

		@param id 商品ID
		"""
		product_detail = resource.get('mall', 'product_detail', {
			'woid': args['woid'],
			'product_id': args['product_id']
		})

		return product_detail
