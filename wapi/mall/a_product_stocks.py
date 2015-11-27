# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
import resource

from db.mall import models as mall_models
from business.mall.realtime_stock import RealtimeStock
from business.mall.shopping_cart import ShoppingCart

class AProductStocks(api_resource.ApiResource):
	"""
	商品库存信息
	"""
	app = 'mall'
	resource = 'product_stocks'


	@param_required([])
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
			realtime_stock = RealtimeStock.from_product_id({
				'product_id': product_id
			})
		elif model_ids:
			model_ids = model_ids.split(",")
			realtime_stock = RealtimeStock.from_product_model_ids({
				'model_ids': model_ids
			})
		else:
			realtime_stock = None

		if realtime_stock:
			result_data.update(realtime_stock.model2stock)

		# 代码来自 get_member_product_info(request) mall/module_api.py
		if 'need_member_info' in args:
			webapp_user = args['webapp_user']
			webapp_owner = args['webapp_owner']
			member = webapp_user.member
			if member:
				result_data['count'] = ShoppingCart.get_for_webapp_user({
					'webapp_owner': webapp_owner,
					'webapp_user': webapp_user
				}).product_count
				result_data['member_grade_id'] = member.grade_id
				_, result_data['discount'] = member.discount
				result_data['usable_integral'] = member.integral
				result_data['is_collect'] = member.is_collect_product(product_id)
				result_data['is_subscribed'] = member.is_subscribed
			else:
				result_data['count'] = 0
				result_data['is_collect'] = False
				result_data['member_grade_id'] = -1
				result_data['discount'] = 100
				result_data['usable_integral'] = 0
				result_data['is_subscribed'] = False

		return result_data

