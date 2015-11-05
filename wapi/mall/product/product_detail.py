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


	@param_required(['id'])
	def get(args):
		"""
		获取商品详情

		@param id 商品ID
		"""
		product_id = args['id']
		product_detail = resource.get('mall', 'product_detail', {
			'oid': 48,
			'product_id': product_id
		})
		return product_detail.to_dict(
									'min_limit',
									'swipe_images_json'
				)
