# -*- coding: utf-8 -*-
from behave import *
import json

from features.steps.steps_db_util import get_area_ids
from features.util import bdd_util
import db.mall.models as mall_models
from db.wzcard import models as wzcard_models


@When(u"{webapp_user_name}提交团购订单")
def step_impl(context, webapp_user_name):
	"""
	@type context: behave.runner.Context
	"""

	args = json.loads(context.text)
	put_order_info = context.put_order_info
	# 处理中文地区转化为id，如果数据库不存在的地区则自动添加该地区
	ship_area = get_area_ids(args.get('ship_area'))

	data = {
		"woid": put_order_info['woid'],
		"module": 'mall',
		"is_order_from_shopping_cart": False,
		"target_api": "order/save",
		"product_ids": put_order_info['product_ids'],
		"promotion_ids": '',
		"product_counts": '1',
		"product_model_names": 'standard',
		"ship_name": args.get('ship_name', "未知姓名"),
		"area": ship_area,
		"ship_id": 0,
		"ship_address": args.get('ship_address', "长安大街"),
		"ship_tel": args.get('ship_tel', "11111111111"),
		"is_use_coupon": "false",
		"is_use_bill": "",
		"bill_type": 0,
		"bill": "",
		"coupon_id": '',
		"message": args.get('customer_message', ''),
		"group2integralinfo": '{}',
		"card_name": '',
		"card_pass": '',
		"xa-choseInterfaces": 2,
		'order_type': 'undefined',
		'group_id': put_order_info['group_id'],
		'activity_id': put_order_info['activity_id']
	}


	if args.has_key("distribution_time"):
		time_str = args.get("distribution_time")
		time_strs = time_str.split(" ")
		data["delivery_time"] = "{} {}".format(bdd_util.get_date_str(time_strs[0]), time_strs[1])

	url = '/wapi/mall/order/?_method=put'
	response = context.client.post(url, data)
	# bdd_util.assert_api_call_success(response)
	context.response = response

	# response结果为: {"errMsg": "", "code": 200, "data": {"msg": null, "order_id": "20140620180559"}}
	if response.body['code'] == 200:
		# context.created_order_id为订单ID
		context.created_order_id = response.data['order_id']

		# 同步更新支付时间
		if mall_models.Order.get(
				order_id=context.created_order_id).status > mall_models.ORDER_STATUS_CANCEL and args.has_key('date'):
			mall_models.Order.update(payment_time=bdd_util.get_datetime_str(args['date'])).dj_where(
				order_id=context.created_order_id).execute()
	else:
		print('**********************团购下单失败*****************')
		print(response.data)
		print('**********************团购下单失败*****************')
		assert False

	if context.created_order_id != -1:
		if 'date' in args:
			mall_models.Order.update(created_at=bdd_util.get_datetime_str(args['date'])).dj_where(
				order_id=context.created_order_id).execute()
		if 'order_id' in args:

			order_has_group = mall_models.OrderHasGroup.select().dj_where(order_id=context.created_order_id).first()
			order_has_group.order_id = args['order_id']
			order_has_group.save()

			context.response.data['order_id'] = args['order_id']
			db_order = mall_models.Order.get(order_id=context.created_order_id)
			if db_order.weizoom_card_money > 0:
				wzcard_has_orders = wzcard_models.WeizoomCardHasOrder.select().dj_where(order_id=db_order.order_id)
				for wzcard_has_order in wzcard_has_orders:
					wzcard_has_order.order_id = args['order_id']
					wzcard_has_order.save()
			db_order.order_id = args['order_id']
			db_order.save()
			if db_order.origin_order_id < 0:
				for order in mall_models.Order.select().dj_where(origin_order_id=db_order.id):
					order.order_id = '%s^%s' % (args['order_id'], order.supplier)
					order.save()
			context.created_order_id = args['order_id']


	context.product_ids = data['product_ids']
	context.product_counts =data['product_counts']
	context.product_model_names = 'standard'



