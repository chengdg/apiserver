# -*- coding: utf-8 -*-
import json

from behave import *

from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
import steps_db_util
import logging

@then(u"{user}能获取订单")
def step_impl(context, user):
	db_order = steps_db_util.get_latest_order()

	response = context.client.get('/wapi/mall/order/', {
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
	logging.info("Context.text: {}".format(expected))
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
	response = context.client.post('/wapi/mall/order/', {
		'woid': context.client.woid,
		'order_id': order_id,
		'action': 'cancel'
	})

	context.tc.assertTrue(200 == response.body['code'])


@then(u"{webapp_user_name}在webapp查看'{order_id}'的物流信息")
def step_impl(context, webapp_user_name, order_id):
	expected_order = json.loads(context.text)
	response = context.client.get('/wapi/mall/express_details/', {
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

