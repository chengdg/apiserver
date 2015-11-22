# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
import resource

from wapi.mall import models as mall_models
from business.mall.product_stocks import ProductStocks

class AProductStocks(api_resource.ApiResource):
	"""
	商品库存信息
	"""
	app = 'mall'
	resource = 'product_stocks'


	@param_required(['woid', 'wuid'])
	def get(args):
		"""
		@param product_id 商品ID
		"""
		product_id = args.get('product_id', None)
		model_ids = args.get('model_ids', None)
		need_member_info = args.get('need_member_info', False)

		#改为从缓存读取库存数据 duhao 2015-08-13
		# response = create_response(200)
		# if product_id:
		# 	response.data = cache_util.get_product_stocks_from_cache(product_id)
		# elif model_ids:
		# 	response.data = cache_util.get_product_stocks_from_cache(model_ids, True)
		# else:
		# 	return create_response(500).get_response()
		

		# return response.get_response()

		result_data = dict()

		#获取商品的库存信息
		if product_id:
			product_stocks = ProductStocks.from_product_id({
				'product_id': product_id
			})
		elif model_ids:
			model_ids = model_ids.split(",")
			product_stocks = ProductStocks.from_product_model_ids({
				'model_ids': model_ids
			})
		else:
			product_stocks = None

		if product_stocks:
			result_data.update(product_stocks.model2stock)

		# 代码来自 get_member_product_info(request) mall/module_api.py
		if 'need_member_info' in args:
			member_info_data = resource.get('member', 'member_product_info', {
				"woid": args['woid'],
				"wuid": args['wuid'],
				"product_id": product_id,
				"member": None
			})
			result_data = dict(result_data, **member_info_data)

		return result_data
