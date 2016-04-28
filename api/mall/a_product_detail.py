# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
from db.mall import models as mall_models
from util import dateutil as utils_dateutil
#import resource
from business.mall.product import Product


class AProductDetail(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'product_detail'


	@param_required(['member', 'product_id'])
	def get(args):
		"""
		获取商品详情

		@param member
		@param product_id
		"""
		product = Product.from_id({
			'woid': args['woid'],
			'member': args['member'],
			'product_id': args['product_id']
		})
		
		return product.to_dict()

