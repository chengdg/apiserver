# -*- coding: utf-8 -*-
import json

from behave import *

from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME

@then(u"{user}能获取商品分类列表")
def step_impl(context, user):
	response = context.client.get('/wapi/mall/product_categories/', {
		'at':context.client.user.token, 
		'woid':context.client.woid
	})
	
	print '-*-' * 20
	print response
	print '-*-' * 20
	expected = json.loads(context.text)
	actual = response.body['data']

	bdd_util.assert_list(expected, actual)
