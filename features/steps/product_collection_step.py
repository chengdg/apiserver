# -*- coding: utf-8 -*-
import json

from behave import *

from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
from db.mall import models as mall_models


@when(u"{weixin_user}收藏{user}的商品到我的收藏")
def step_impl(context, weixin_user,user):
	product_info = json.loads(context.text)
	webapp_owner_id = context.webapp_owner_id
	product_name = product_info['name']
	print '>>>>>>>>>>>>>>>>>>>>>',product_name
	product = mall_models.Product.get(owner=webapp_owner_id, name=product_name)

	response = context.client.put('/wapi/member/wish_product/', {
		'product_id': product.id
	})
	
	expected = json.loads(context.text)
	actual = response.body['data']


@then(u"{weixin_user}能获得我的收藏")
def step_impl(context, weixin_user):
	expected = json.loads(context.text)
	webapp_owner_id = context.webapp_owner_id
	response = context.client.get('/wapi/member/wish_products/', {
	})
	
	expected = json.loads(context.text)
	actual = response.body['data']['products']
	bdd_util.assert_list(expected, actual)
