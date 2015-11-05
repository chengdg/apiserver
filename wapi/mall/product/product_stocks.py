# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
import resource

from wapi.mall import models as mall_models

class ProductStocks(api_resource.ApiResource):
	"""
	商品库存信息
	"""
	app = 'mall'
	resource = 'product_stocks'


	@param_required(['woid', 'wuid', 'product_id'])
	def get(args):
		"""
		@param product_id 商品ID
		"""
		product_id = args['product_id']
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

		print '*' * 20
		print args
		print '*' * 20
		if product_id:
			models = mall_models.ProductModel.select().dj_where(product=product_id, is_deleted=False)
			print '*' * 20
			print models
			print '*' * 20
		elif model_ids:
			model_ids = model_ids.split(",")
			models = mall_models.ProductModel.select().dj_where(id__in=model_ids, is_deleted=False)
		else:
			models = []

		for model in models:
			model_data = dict()
			model_data["stocks"] = model.stocks
			model_data["stock_type"] = model.stock_type
			result_data[model.id] = model_data

		# 代码来自 get_member_product_info(request) mall/module_api.py
		if need_member_info == '1':
			member_info_data = resource.get('member', 'member_product_info', {
				"woid": args['woid'],
				"wuid": args['wuid'],
				"product_id": product_id,
				"member": None
			})
			result_data = dict(result_data, **member_info_data)

		return result_data
