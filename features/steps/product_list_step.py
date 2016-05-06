# -*- coding: utf-8 -*-

from behave import *

@then(u"{user}'{action}'获得商品搜索框")
def step_impl(context, user, action):
	response = context.client.get('/mall/products/?category_id=0')
	data = response.data
	expected = True if action == u'能' else False
	actual = data['mall_config']['show_product_search']
	assert expected == actual
