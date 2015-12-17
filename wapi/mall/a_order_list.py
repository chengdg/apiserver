# -*- coding: utf-8 -*-

import copy
from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from utils import dateutil as utils_dateutil
import resource
from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
from core.cache import utils as cache_utils
from business.mall.order import Order
from business.mall.order_products import OrderProducts


class AOrderList(api_resource.ApiResource):
	"""
	订单列表
	"""
	app = 'mall'
	resource = 'order_list'

	@param_required(['type'])
	def get(args):
		"""
		会员订单列表

		@param id 商品ID
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		data = {
			'info': 'order_list'
		}

		orders = Order.get_orders_for_webapp_user({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user
		})

		order_datas = []
		for order in orders:
			data = {
				'id': order.id,
				'order_id': order.order_id,
				'status': order.status,
				'pay_interface_type': order.pay_interface_type,
				'created_at': order.created_at.strftime('%Y.%m.%d %H:%M'),
				'final_price': order.final_price,
				'has_sub_order': order.has_sub_order,
				'express_number': order.express_number,
				'review_is_finished': False,
				'products': []
			}

			order_products = OrderProducts.get_for_order({
				'webapp_owner': webapp_owner,
				'webapp_user': webapp_user,
				'order': order
			})

			total_product_count = 0
			for order_product in order_products.products:
				product_data = {
					'id': order_product.id,
					'name': order_product.name,
					'purchase_count': order_product.purchase_count,
					'thumbnails_url': order_product.thumbnails_url,
					'model': order_product.model.to_dict()
				}
				total_product_count += order_product.purchase_count
				data['products'].append(product_data)

			data['product_count'] = total_product_count
			order_datas.append(data)

		return {
			'orders': order_datas
		}


