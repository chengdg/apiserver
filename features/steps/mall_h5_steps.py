# -*- coding: utf-8 -*-
import json

from behave import *

from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
from db.mall import models as mall_models

@when(u"{webapp_user_name}浏览{webapp_owner_name}的webapp的'{category_name}'商品列表页")
def step_impl(context, webapp_user_name, webapp_owner_name, category_name):
	if category_name == u'全部':
		category_id = 0
	else:
		category = mall_models.ProductCategory.get(name=category_name)
		category_id = category.id

	url = '/wapi/mall/products/?woid=%s&category_id=%s' % (context.webapp_owner_id, category_id)
	response = context.client.get(bdd_util.nginx(url), follow=True)
	context.response = response

@then(u"{webapp_user_name}获得webapp商品列表")
def step_impl(context, webapp_user_name):
	if context.table:
		expected = []
		for promotion in context.table:
			promotion = promotion.as_dict()
			expected.append(promotion)
	else:
		expected = json.loads(context.text)
	actual = context.response.data['products']
	bdd_util.assert_list(expected, actual)