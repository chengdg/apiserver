# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
#import resource

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
		product_ids = args.get('product_ids', None)
		need_member_info = args.get('need_member_info', False)

		result_data = dict()

		#获取商品的库存信息
		if product_ids:
			for product_id in product_ids.split('_'):
				realtime_stock = RealtimeStock.from_product_id({
					'product_id': product_id
				})
				if realtime_stock:
					merged_stock_info = {
						'stock_type': mall_models.PRODUCT_STOCK_TYPE_LIMIT,
						'stocks': 0
					}
					for model, stock_info in realtime_stock.model2stock.items():
						if stock_info['stock_type'] == mall_models.PRODUCT_STOCK_TYPE_UNLIMIT:
							merged_stock_info['stock_type'] = mall_models.PRODUCT_STOCK_TYPE_UNLIMIT
							merged_stock_info['stocks'] = -1
							break
						else:
							merged_stock_info['stocks'] = merged_stock_info['stocks'] + stock_info.get('stocks', 0)

				result_data.update({product_id: merged_stock_info})
		else:
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

			if 'need_member_info' in args:
				AProductStocks.__fill_member_info(result_data, product_id, args)

		return result_data

	@staticmethod
	def __fill_member_info(result_data, product_id, args):
		"""
		向result_data中填充会员信息
		"""
		# 代码来自 get_member_product_info(request) mall/module_api.py
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
			result_data['is_collect'] = webapp_user.is_collect_product(product_id)
			result_data['is_subscribed'] = member.is_subscribed
		else:
			result_data['count'] = 0
			result_data['is_collect'] = False
			result_data['member_grade_id'] = -1
			result_data['discount'] = 100
			result_data['usable_integral'] = 0
			result_data['is_subscribed'] = False
