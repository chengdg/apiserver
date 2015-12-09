# -*- coding: utf-8 -*-
import json

from behave import *

from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
import steps_db_util


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
	error_data = context.response
	context.tc.assertTrue(200 != error_data.status_code)
	response_msg = error_data.body['errMsg']
	context.tc.assertEquals(error_msg, response_msg)
