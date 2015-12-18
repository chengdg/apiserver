# -*- coding: utf-8 -*-
import json
import time

from behave import *

from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
from db.mall import models as mall_models
import logging

@when(u"{webapp_user}查看'{text}'")
def step_visit_product_review(context, webapp_user, text):
	pass

@then(u"{webapp_user}成功获取'{text}'列表")
def step_product_review_should(context, webapp_user, text):
	response = context.client.get('/wapi/member/reviewed_products/', {
	})
	
	expected = json.loads(context.text)
	#actual = response.body['data']['reviewed_products']
	# 实际的输出
	actual = []
	product_review_list = response.body['data']['reviewed_products']
	for i in product_review_list:
		product_review = {}
		product_review['review_detail'] = i['review_detail']
		product_review['product_name'] = i['product']['name']
		actual.append(product_review)
	print("-"*10, 'actual', "-"*10, actual)
	print("-"*10, 'expected', "-"*10, expected)
	bdd_util.assert_list(expected, actual)


@When(u"{webapp_user}完成订单'{order_code}'中'{product_name}'的评价")
def step_finished_a_product_review(context, webapp_user, order_code, product_name):
	"""
	完成订单评价

	@see 原Weapp中`features/steps/webapp_product_review_steps.py`
	"""
	context_dict = json.loads(context.text)

	url = '/wapi/member/review_product/?_method=put'
	#url = '/webapp/api/project_api/call/'
	# 原始源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
	order_has_product = bdd_util.get_order_has_product(order_code, product_name)
	params = {}
	params.update(context_dict)
	params.update({
		'woid': context.webapp_owner_id,
		'order_id': order_has_product.order_id,
		'product_id': order_has_product.product_id,
		'order_has_product_id': order_has_product.id,
	})
	# 输入
	#data['target_api'] = 'product_review/create'
	#data['module'] = 'mall'
	has_picture = context_dict.get('picture_list', None)
	if has_picture:
		params['picture_list'] = str(has_picture)
	bdd_util.assert_api_call_success(context.client.post(url, params))

@then(u"{webapp_user}成功获取商品评价后'感谢评价'页面")
def step_get_user_thanks_page(context, webapp_user):
	pass