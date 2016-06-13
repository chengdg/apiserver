# -*- coding: utf-8 -*-
"""@package apimall.a_order
订单API

"""

import copy
from datetime import datetime

from eaglet.core import api_resource
from core.exceptionutil import unicode_full_stack
import settings
from eaglet.utils.lock import wapi_lock
from eaglet.decorator import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from util import dateutil as utils_dateutil
#import resource
from api.mall.a_purchasing import APurchasing as PurchasingApiResource
from eaglet.core.cache import utils as cache_utils
from business.mall.order_factory import OrderFactory, OrderResourcesException
from business.mall.purchase_info import PurchaseInfo
from business.mall.pay_interface import PayInterface
from business.mall.order import Order
from eaglet.core import watchdog
from business.spread.member_spread import MemberSpread
import logging

class AOrder(api_resource.ApiResource):
	"""
	订单
	"""
	app = 'mall'
	resource = 'order'

	@param_required(['ship_name', 'ship_address', 'ship_tel', 'order_type', 'xa-choseInterfaces'])
	@wapi_lock()
	def put(args):
		"""
		下单接口

		@param id 商品ID
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		refueling_order = args.get('refueling_order', '')

		# print('---------webapp_user_id:',webapp_user.id)
		# if not get_wapi_lock(lockname='order_put_' + str(webapp_user.id), lock_timeout=1):
		# 	watchdog.alert('wapi接口被刷,wapi:%s,webapp_user_id:%s' % ('mall.order_put', str(webapp_user.id)))
		# 	reason_dict = {
		# 		"is_success": False,
		# 		"msg":  u'请勿短时间连续下单',
		# 		"type": "coupon"    # 兼容性type
		# 	}
		# 	return 500, {'detail': [reason_dict]}

		#解析购买参数
		purchase_info = PurchaseInfo.parse({
			'request_args': args
		})

		validate_success = purchase_info.validate()

		if not validate_success:
			return 500, {'detail': ''}

		if purchase_info.is_force_purchase:
			webapp_user.set_force_purchase()

		try:
			order_factory = OrderFactory.get({
				"webapp_owner": webapp_owner,
				"webapp_user": webapp_user
			})
			order = order_factory.create_order(purchase_info)
		except OrderResourcesException as e:
			# 实际上detail是reason列表
			return 500, {'detail': e.value}
		except:
			watchdog.alert(unicode_full_stack())
			return 500, {'detail': ''}

		pay_url_info = None
		if order:
			if purchase_info.used_pay_interface_type != '-1':
				try:
					pay_interface = PayInterface.from_type({
						"webapp_owner": webapp_owner,
						"pay_interface_type": purchase_info.used_pay_interface_type
					})
					pay_url_info = pay_interface.get_pay_url_info_for_order(order)
				except:
					notify_message = u"order_id:{}, used_pay_interface_type:{}, cause:\n{}".format(order.id,  purchase_info.used_pay_interface_type, unicode_full_stack())
					watchdog.error(notify_message)
					print notify_message

		data = {
			'order_id' : order.order_id,
			'id' : order.id,
			'final_price' : round(order.final_price, 2)
		}
		if pay_url_info:
			data['pay_url_info'] = pay_url_info

		#处理分享来的订单

		try:
			url = args.get('url', None)
			if url:
				MemberSpread.record_order_from_spread({
					'order_id' : order.id,
					'webapp_user' : webapp_user,
					'url' : url
					})
		except:
			pass


		return data

	@param_required(['order_id', 'action'])
	@wapi_lock()
	def post(args):
		"""
		更改订单状态
		@todo 目前取消订单和确认收货都是通过此接口，需要分离
		"""
		# if not get_wapi_lock(lockname='order_post_' + str(args['webapp_user'].id), lock_timeout=2):
		# 	watchdog.alert('wapi接口被刷,wapi:%s,webapp_user_id:%s' % ('mall.order_post', str(args['webapp_user'].id)))
		# 	reason_dict = {
		# 		"is_success": False,
		# 		"msg":  u'请勿短时间连续下单',
		# 		"type": "coupon"    # 兼容性type
		# 	}
		# 	return 500, {'detail': [reason_dict]}

		# 兼容修改价格后订单从支付模块返回的跳转（支付模块会添加edit_money）
		order_id = args['order_id'].split('-')[0]

		try:
			order = Order.from_id({
				'webapp_user': args['webapp_user'],
				'webapp_owner': args['webapp_owner'],
				'order_id': order_id
			})

			action = args['action']

			validate_result, reason = order.validate_order_action(action, args['webapp_user'].id)

			msg = u"apiserver中修改订单状态失败, order_id:{}, action:{}, cause:\n{}".format(args['order_id'], args['action'], reason)
			watchdog.info(msg)

			if not validate_result:
				return 500, {'msg': reason}

			if action == 'cancel':
				order.cancel()
			elif action == 'finish':
				order.finish()
		except:
			notify_message = u"apiserver中修改订单状态失败, order_id:{}, action:{}, cause:\n{}".format(args['order_id'], args['action'], unicode_full_stack())
			watchdog.alert(notify_message)
			return 500, ''



	# @param_required(['order_id'])
	# def delete(args):
	# 	"""
	# 	取消订单
	# 	"""
	# 	order = Order.from_id({
	# 		'webapp_user': args['webapp_user'],
	# 		'webapp_owner': args['webapp_owner'],
	# 		'order_id': args['order_id']
	# 	})
	#
	# 	order.cancel()
	# 	return {
	# 		'success': True
	# 	}



	@staticmethod
	def to_dict(order):
		order_dict = order.to_dict('latest_express_detail', 'products', 'is_group_buy', 'order_group_info')
		api_keys = [
			"buyer_name",
			"coupon_money",
			"integral",
			"ship_area",
			"member_grade_id",
			"edit_money",
			"id",
			"pay_interface_name",
			"ship_name",
			"has_sub_order",
			"has_multi_sub_order",
			"sub_orders",
			"product_price",
			"member_grade_discount",
			"supplier",
			"latest_express_detail",
			"type",
			"integral_each_yuan",
			"final_price",
			"status",
			"postage",
			"ship_address",
			"pay_interface_type",
			"order_id",
			"integral_money",
			"ship_tel",
			"origin_order_id",
			"coupon_id",
			"customer_message",
			"webapp_id",
			"promotion_saved_money",
			"express_number",
			"webapp_user_id",
			"products",
			"status_text",
			"created_at",
			"weizoom_card_money",
			"red_envelope",
			"red_envelope_created",
			"pay_info",
			"bill_type",
			"bill",
			"delivery_time",
			"is_group_buy",
			"order_group_info",
		]

		data = {}
		for key in api_keys:
			data[key] = order_dict.get(key)
		return {
			"order": data
		}

	@param_required(['order_id'])
	def get(args):

		# 兼容修改价格后订单从支付模块返回的跳转（支付模块会添加edit_money）
		order_id = args['order_id'].split('-')[0].split('^')[0]

		order = Order.from_id({
			'webapp_owner': args['webapp_owner'],
			'webapp_user': args['webapp_user'],
			'order_id': order_id
		})

		order_data = AOrder.to_dict(order)
		order_data.update({'mall_type': args['webapp_owner'].user_profile.webapp_type})

		# 调试bug 9094
		if order_id == '20160314103614898':
			try:
				import json

				json.dumps(order_data)
			except:
				msg = unicode_full_stack()
				print('--------abcdef',msg)
				watchdog.info(msg, log_type='online')

		return order_data