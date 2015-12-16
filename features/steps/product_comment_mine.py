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