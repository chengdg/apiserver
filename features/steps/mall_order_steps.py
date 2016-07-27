# -*- coding: utf-8 -*-
import json
from db.mall import models as mall_models
from behave import *

from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
import steps_db_util
import logging

@then(u"{user}能获取订单")
def step_impl(context, user):
	db_order = steps_db_util.get_latest_order()

	response = context.client.get('/mall/order/', {
		'woid': context.client.woid,
		'order_id': db_order.order_id
	})

	order = response.body['data']['order']

	expected = json.loads(context.text)
	bdd_util.assert_dict(expected, order)


@then(u"{webapp_user_name}获得创建订单失败的信息'{error_msg}'")
def step_impl(context, webapp_user_name, error_msg):
	context.tc.assertTrue(200 != context.response.body['code'])
	
	data = context.response.data
	response_msg = data.get('msg', None)
	#logging.info("data: {}".format(data))
	if not response_msg:
		response_msg = data['detail'][0]['msg']
	context.tc.assertEquals(error_msg, response_msg)


@then(u"{webapp_user_name}获得创建订单失败的信息")
def step_impl(context, webapp_user_name):
	error_data = context.response
	context.tc.assertTrue(200 != context.response.body['code'])

	expected = json.loads(context.text)
	#logging.info("Context.text: {}".format(expected))
	webapp_owner_id = context.webapp_owner_id
	for detail in expected['detail']:
		product = steps_db_util.get_product_by_prouduct_name(owner_id=webapp_owner_id, name=detail['id'])
		detail['id'] = product.id

		if 'model' in detail:
			detail['model_name'] = steps_db_util.get_product_model_keys(detail['model'])
			del detail['model']

	actual = context.response.data

	logging.info("actual: {}".format(actual))
	bdd_util.assert_dict(expected, actual)


@when(u"{webapp_user_name}取消订单'{order_id}'")
def step_impl(context, webapp_user_name, order_id):
	logging.info('webapp_user_name: {}'.format(webapp_user_name))
	response = context.client.post('/mall/order/', {
		'woid': context.client.woid,
		'order_id': order_id,
		'action': 'cancel'
	})

	context.tc.assertTrue(200 == response.body['code'])


@when(u"{webapp_user_name}确认收货订单'{order_id}'")
def step_impl(context, webapp_user_name, order_id):
	logging.info('webapp_user_name: {}'.format(webapp_user_name))
	response = context.client.post('/mall/order/', {
		'woid': context.client.woid,
		'order_id': order_id,
		'action': 'finish'
	})

	context.tc.assertTrue(200 == response.body['code'])

@then(u"{webapp_user_name}'{is_can}'取消订单'{order_id}'")
def step_impl(context, webapp_user_name, is_can, order_id):
	logging.info('webapp_user_name: {}'.format(webapp_user_name))
	response = context.client.get('/mall/order/', {
		'woid': context.client.woid,
		'order_id': order_id
	})

	order = response.body['data']['order']
	if is_can == u'能':
		context.tc.assertTrue(order['status_text'] == u'待支付')
	elif is_can == u'不能':
		context.tc.assertTrue(order['status_text'] != u'待支付')
	else:
		context.tc.assertTrue(1 == 0)


@then(u"{webapp_user_name}在webapp查看'{order_id}'的物流信息")
def step_impl(context, webapp_user_name, order_id):
	expected_order = json.loads(context.text)
	response = context.client.get('/mall/express_details/', {
		'woid': context.client.woid,
		'order_id': order_id
	})
	context.tc.assertTrue(200 == response.body['code'])

	actual_order = response.body['data']
	actual_order = {
		'order_id': actual_order['order_id'],
		'logistics': actual_order['express_company_name'],
		'number': actual_order['express_number'],
		'status': actual_order['status']
	}

	bdd_util.assert_dict(expected_order, actual_order)


@then(u"{webapp_user_name}不能'{action}'订单'{order_id}'")
def step_impl(context, webapp_user_name, action, order_id):

	if action == '支付':
		pay_url = '/pay/pay_result/?_method=put'
		data = {
			'pay_interface_type': 2,
			'order_id': context.created_order_id
		}
		response = context.client.post(pay_url, data)
		context.tc.assertTrue(200 != response.body['code'])

		a_action = ''

	elif action == '取消':
		a_action = 'cancel'
	elif action == '确认收货':
		a_action = 'finish'
	else:
		a_action = ''
	if a_action:
		response = context.client.post('/mall/order/', {
			'woid': context.client.woid,
			'order_id': order_id,
			'action': a_action
		})

	context.tc.assertTrue(200 != response.body['code'])


@step(u"{webapp_user}设置订单列表分页查询参数")
def step_impl(context, webapp_user):
	"""
	@type context: behave.runner.Context
	"""
	context.count_per_page = json.loads(context.text)['count_per_page']
	context.cur_page = json.loads(context.text)['cur_page']


@then(u"{webapp_user_name}查看个人中心'{order_type}'订单列表")
def step_visit_personal_orders(context, webapp_user_name, order_type):
	if order_type == u'全部':
		status = -1
	elif order_type == u'待支付':
		status = 0
	elif order_type == u'待发货':
		status = 3
	elif order_type == u'待收货':
		status = 4
	else:
		status = -1

	expected = json.loads(context.text)
	actual = []

	if hasattr(context, 'count_per_page'):
		count_per_page = context.count_per_page
		del context.count_per_page

	else:
		count_per_page = 100

	if hasattr(context, 'cur_page'):
		cur_page = context.cur_page
		del context.cur_page
	else:
		cur_page = 1

	url = '/mall/order_list/?woid={}&order_type={}&cur_page={}&count_per_page={}'.format(context.webapp_owner_id, status,cur_page,count_per_page)
	response = context.client.get(bdd_util.nginx(url), follow=True)

	orders = response.data['orders']
	import datetime
	for actual_order in orders:
		if actual_order['status'] != status and status != -1:
			continue
		order = {}
		order['final_price'] = actual_order['final_price']
		order['products'] = []
		order['counts'] = actual_order['product_count']
		order['status'] = mall_models.ORDERSTATUS2MOBILETEXT[actual_order['status']]
		order['pay_interface'] = mall_models.PAYTYPE2NAME[actual_order['pay_interface_type']]
		order['created_at'] = actual_order['created_at']
		order['pay_info'] = actual_order['pay_info']
		order['order_no'] = actual_order['order_id']
		order['order_id'] = actual_order['order_id']
		order['is_group_buying'] = 'true' if  actual_order['is_group_buy'] else 'false'

		# BBD中购买的时间再未指定购买时间的情况下只能为今天
		created_at = datetime.datetime.strptime(actual_order['created_at'], '%Y.%m.%d %H:%M')
		if created_at.date() == datetime.date.today():
			order['created_at'] = u'今天'

		for i, product in enumerate(actual_order['products']):
			# 列表页面最多显示3个商品
			a_product = {}
			a_product['name'] = product['name']
			# a_product['price'] = product.total_price
			order['products'].append(a_product)
		actual.append(order)
	bdd_util.assert_list(expected, actual)
