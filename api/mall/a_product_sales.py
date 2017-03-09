# -*- coding: utf-8 -*-
import json

from eaglet.core import api_resource
from eaglet.decorator import param_required
#import resource

from db.mall import models as mall_models
from business.mall.realtime_stock import RealtimeStock
from business.mall.product_sales import ProductSales

class AProductSales(api_resource.ApiResource):
	"""
	商品库存信息
	"""
	app = 'mall'
	resource = 'product_sales'

	@param_required([])
	def get(args):
		"""
		@param product_id 商品ID
		"""
		product_ids = args.get('product_ids', '[]')
		product_ids = json.loads(product_ids)
		bussiness_models = ProductSales().get_product_sales_by_ids(product_ids=product_ids)
		data = []
		for model in bussiness_models:
			data.append({
				"id": model.product_id,
				'sales': model.sales
			})
		return data
		