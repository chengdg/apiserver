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
	response = context.client.get('/member/reviewed_products/', {
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

	url = '/member/review_product/?_method=put'
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
	#bdd_util.assert_api_call_success(context.client.post(url, params))
	response = context.client.post(url,params)

	if response.body['code'] != 200:
		context.comment_status = False
	else:
		status = response.body['data']['status']
		if int(status) == 1:
			context.comment_status = True
			has_waiting_review = response.body['data']['has_waiting_review']
			if int(has_waiting_review) == 1:
				context.has_waiting_review = True
			else:
				context.has_waiting_review = False
		else:
			context.comment_status = False


@then(u"{webapp_user}成功获取商品评价后'感谢评价'页面")
def step_get_user_thanks_page(context, webapp_user):
	expected = json.loads(context.text)
	actual = []

	if hasattr(context,'has_waiting_review'):
		if context.has_waiting_review:
			actual.append({
				"title1": "继续评价",
				"title2": "返回首页"
				})
		else:
			actual.append({
				"title2": "返回首页"
				})
		bdd_util.assert_list(expected, actual)

@then(u"订单'{order_no}'中'{product_name}'的评商品评价提示信息'{review_status}'")
def step_get_user_publish_review(context, order_no, product_name, review_status):
	if hasattr(context,'comment_status'):
		comment_status = context.comment_status
		if review_status == u'发表评价失败':
			context.tc.assertTrue(False == comment_status)
	else:
		pass

@then(u"{webapp_user}获取订单'{order_code}'中'{product_name}'的追加晒图页面")
def step_a_waiting_review_product(context, webapp_user, order_code, product_name):
	"""
	完成订单评价

	@see 原Weapp中`features/steps/webapp_product_review_steps.py`
	"""
	context_dict = json.loads(context.text)

	url = '/member/review_product/?_method=get'
	# 原始源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
	order_has_product = bdd_util.get_order_has_product(order_code, product_name)
	params = {}
	#params.update(context_dict)
	params.update({
		'woid': context.webapp_owner_id,
		'order_id': order_has_product.order_id,
		'product_id': order_has_product.product_id,
		'order_has_product_id': order_has_product.id,
	})
	
	response = context.client.get(url,params)
	response_data = response.body['data']
	product_review = response_data['reviewed_product']
	actual = {}
	actual['product_score'] = product_review['product_score']
	actual['review_detail'] = product_review['review_detail']
	actual['picture_list'] = product_review['reviewed_product_pictures']
	
	bdd_util.assert_dict(context_dict, actual)

@when(u"{webapp_user}完成订单'{order_code}'中'{product_name}'的追加晒图评价")
def step_a_waiting_review_product_picture(context, webapp_user, order_code, product_name):
	context_dict = json.loads(context.text)
	has_picture = context_dict.get('picture_list', None)
	

	url = '/member/review_product/?_method=post'
	# 原始源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
	order_has_product = bdd_util.get_order_has_product(order_code, product_name)
	params = {}
	if has_picture:
		params['picture_list'] = str(has_picture)
	params.update({
		'woid': context.webapp_owner_id,
		'order_id': order_has_product.order_id,
		'product_id': order_has_product.product_id,
		'order_has_product_id': order_has_product.id,
	})
	response = context.client.post(url,params)
	