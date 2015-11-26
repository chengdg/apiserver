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
