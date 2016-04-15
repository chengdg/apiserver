# -*- coding: utf-8 -*-

import copy
from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from utils import dateutil as utils_dateutil
#import resource
from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
from core.cache import utils as cache_utils
from business.mall.order import Order
from business.mall.order_products import OrderProducts
from business.mall.review.waiting_review_order import WaitingReviewOrder


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

		@param type
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

		# 过滤已取消的团购订单,但优惠抵扣的显示
		orders = filter(lambda order: not(order.is_group_buy and order.status == mall_models.ORDER_STATUS_CANCEL) or order.pay_interface_type ==  mall_models.PAY_INTERFACE_PREFERENCE ,orders)

		order_datas = []
		for order in orders:
			#子订单不显示在订单列表中
			if order.origin_order_id > 0:
				continue

			waiting_review_order = WaitingReviewOrder.get_for_order({
				'webapp_owner': webapp_owner,
				'order': order,
				'webapp_user': webapp_user
				})

			review_is_finished = waiting_review_order.reviewed
			
			data = {
				'id': order.id,
				'order_id': order.order_id,
				'status': order.status,
				'pay_interface_type': order.pay_interface_type,
				'created_at': order.created_at.strftime('%Y.%m.%d %H:%M'),
				'final_price': order.final_price,
				'has_sub_order': order.has_sub_order,
				'has_multi_sub_order': order.has_multi_sub_order,
				'express_number': order.express_number,
				'review_is_finished': review_is_finished,
				'red_envelope': order.red_envelope,
				'red_envelope_created': order.red_envelope_created,
				'products': [],
				'is_group_buy': order.is_group_buy,
				'order_group_info': order.order_group_info
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
					'model': order_product.model.to_dict() if order_product.model else None
				}
				total_product_count += order_product.purchase_count
				data['products'].append(product_data)

			data['product_count'] = total_product_count

			data['pay_info'] = order.pay_info
			order_datas.append(data)


		return {
			'orders': order_datas
		}


