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

	url = '/mall/products/?woid=%s&category_id=%s' % (context.webapp_owner_id, category_id)
	response = context.client.get(bdd_util.nginx(url), follow=True)
	context.response = response




@when(u"{webapp_user}设置商品列表分页查询参数")
def step_impl(context, webapp_user):
	args = json.loads(context.text)
	context.count_per_page = args['count_per_page']
	context.cur_page = args['cur_page']
	category_name = args.get('categories','')
	if category_name:
		if category_name == u"全部":
			context.category_id = 0
		else:
			context.category_id = mall_models.ProductCategory.select().dj_where(name=category_name).first().id
		print('---------p',category_name,context.category_id)

	# context.category_id = args['count_per_page']


@then(u"{webapp_user_name}获得webapp商品列表")
def step_impl(context, webapp_user_name):
	if context.table:
		expected = []
		for promotion in context.table:
			promotion = promotion.as_dict()
			expected.append(promotion)
	else:
		expected = json.loads(context.text)

	if hasattr(context, 'count_per_page'):
		count_per_page = context.count_per_page
		del context.count_per_page

	else:
		count_per_page = 100

	if hasattr(context, 'category_id'):
		category_id = context.category_id
		print('---------category_id',category_id)
		del context.category_id

	else:
		category_id = 100

	if hasattr(context, 'cur_page'):
		cur_page = context.cur_page
		del context.cur_page
	else:
		cur_page = 1

	if hasattr(context, 'searching_product_name'):
		searching_product_name = context.searching_product_name
		del searching_product_name
	else:
		searching_product_name = ''

	url = '/mall/products/?woid={}&category_id={}&product_name={}&cur_page={}&count_per_page={}'.format(context.webapp_owner_id, category_id, searching_product_name,cur_page,count_per_page)

	response = context.client.get(bdd_util.nginx(url), follow=True)



	actual = response.data['products']
	print('---------------ac',actual)
	for product in actual:
		product['price'] = float('%.2f' % float(product['display_price']))
	bdd_util.assert_list(expected, actual)


	# for product in actual:
	# 	product['price'] = float('%.2f' % float(product['display_price']))
	#
	# if hasattr(context, 'searching_product_name') and context.searching_product_name:
	# 	searching_product_name = context.searching_product_name
	# 	url = '/mall/products/?woid=%s&category_id=%s&product_name=%s' % (context.webapp_owner_id, 0,searching_product_name)
	# 	response = context.client.get(bdd_util.nginx(url), follow=True)
	# 	actual = response.data['products']
	# 	context.searching_product_name = None
	# else:
	# 	actual = context.response.data['products']
	# for product in actual:
	# 	product['price'] = float('%.2f' % float(product['display_price']))
	# bdd_util.assert_list(expected, actual)