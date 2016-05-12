# -*- coding: utf-8 -*-

from behave import *
import json

from features.util import bdd_util


@then(u"{user}'{action}'获得商品搜索框")
def step_impl(context, user, action):
	response = context.client.get('/mall/products/?category_id=0')
	data = response.data
	expected = True if action == u'能' else False
	actual = data['mall_config']['show_product_search']
	assert expected == actual


@then(u"{user}获得搜索记录")
def step_impl(context, user):
	response = context.client.get('/mall/product_search_records/')
	actual = response.data['records']
	expected = json.loads(context.text)['record']
	bdd_util.assert_list(expected, actual)


@when(u"{user}搜索商品")
def step_impl(context, user):
	product_name = json.loads(context.text)['product_name']
	context.searching_product_name = product_name


@when(u"{user}'清除'搜索记录")
def step_impl(context, user):
	context.client.post('/mall/product_search_records/?_method=delete')

