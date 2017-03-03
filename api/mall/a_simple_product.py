# -*- coding: utf-8 -*-
import json
import settings
from business.mall.allocator.order_group_buy_resource_allocator import GroupBuyOPENAPI
from eaglet.core import api_resource
from eaglet.decorator import param_required
from db.mall import models as mall_models
from util import dateutil as utils_dateutil
#import resource
from business.mall.simple_product import SimpleProduct
from business.mall.product_limit_zone_template import ProductLimitZoneTemplate
from business.mall.supplier_postage_config import SupplierPostageConfig
from business.mall.review.product_reviews import ProductReviews

from eaglet.utils.resource_client import Resource
from eaglet.core import watchdog
from eaglet.utils.resource_client import Resource


class AProduct(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'product_simple'

	@param_required(['product_id'])
	def get(args):
		"""
		获取简单商品详情

		@param product_id 商品ID

		"""

		product_id = args['product_id']
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']

		# param_data = {'pid': product_id, 'woid': webapp_owner.id, 'member_id': webapp_user.member.id}

		product = SimpleProduct(None).from_id(webapp_owner, product_id)
		
		return product
