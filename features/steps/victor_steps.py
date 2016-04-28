#coding: utf8
"""@package features.steps.victor_steps
调BDD的step，未来会合并到mall_*_steps.py中

Contact: gaoliqi@weizoom.com
"""

import json
import logging

from behave import *

from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
from db.mall import models as mall_models
from db.mall import promotion_models
from db.member import models as member_models
from .steps_db_util import (
		get_custom_model_id_from_name, get_product_model_keys, get_area_ids
)

@Given(u"{web_user}已有的订单")
def step_impl(context, web_user):
	"""
	检查已有订单

	@todo **建议**将`Given jobs已有的订单`改成`xxx购买jobs的商品`这种step.
	"""
	args = json.loads(context.text)
	# 转换成2个`When xxx购买jobs的商品`的step
	new_step = u'''
		Given %s登录系统:weapp
		And %s已添加支付方式:weapp
			"""
			[{
				"type": "货到付款",
				"is_active": "启用"
			}]
			"""
		'''% (web_user, web_user)
	logging.info("Converted step:\n %s" % new_step)
	context.execute_steps(new_step)

	last_buyer = None
	for order in args:
		buyer = order['member']
		if buyer != last_buyer:
			# login first if not logged-in
			new_step = u'''When %s访问%s的webapp'''% (buyer, web_user)
			logging.info("Converted step:\n %s" % new_step)
			context.execute_steps(new_step)
			last_buyer = buyer

		products = order['products']
		order_id = order['order_no']
		new_step = u'''When %s购买%s的商品
			"""
			{
				"pay_type": "货到付款",
				"order_id": "%s",
				"products": %s
			}
			"""
		''' % (buyer, web_user, order_id, json.dumps(products))
		logging.info("Converted step:\n %s" % new_step)
		context.execute_steps(new_step)
	
	return

# @When(u"{webapp_user}完成订单'{order_code}'中'{product_name}'的评价包括'{has_picture}'")
# def step_finished_a_product_review(context, webapp_user, order_code, product_name, has_picture):
# 	"""
# 	完成订单评价

# 	@see 原Weapp中`features/steps/webapp_product_review_steps.py`
# 	"""
# 	context_dict = json.loads(context.text)

# 	url = '/member/review_product/?_method=put'
# 	#url = '/webapp/api/project_api/call/'
# 	# 原始源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
# 	order_has_product = bdd_util.get_order_has_product(order_code, product_name)
# 	params = {}
# 	params.update(context_dict)
# 	params.update({
# 		'woid': context.webapp_owner_id,
# 		'order_id': order_has_product.order_id,
# 		'product_id': order_has_product.product_id,
# 		'order_has_product_id': order_has_product.id,
# 	})
# 	# 输入
# 	#data['target_api'] = 'product_review/create'
# 	#data['module'] = 'mall'
# 	has_picture = context_dict.get('picture_list', None)
# 	if has_picture:
# 		params['picture_list'] = str(has_picture)
# 	bdd_util.assert_api_call_success(context.client.post(url, params))
# 	return


@Then(u"{webapp_user}在商品详情页成功获取'{product_name}'的评价列表")
def step_webapp_user_get_product_review(context, webapp_user, product_name):
	"""
	@see 原Webapp的`webapp_product_review_steps.py`
	"""
	product = bdd_util.get_product_by(product_name)
	url = "/mall/product/"
	#response = context.client.get(bdd_util.nginx(url), follow=True)
	response = context.client.get(url, {
			# 'woid': context.webapp_owner_id,
			'product_id': product.id
		})
	bdd_util.assert_api_call_success(response)	

	data = response.data
	logging.debug('response.data: {}'.format(data))
	product_review_list = data['product_reviews']
	actual = []
	if product_review_list:
		for i in product_review_list:
			data = {}
			#data['member'] = i.member_name
			member = bdd_util.get_member_by_id(i['member_id'])
			data['member'] = member.username
			data['review_detail'] = i['review_detail']
			actual.append(data)
	else:
		actual.append({})

	expected = json.loads(context.text)
	bdd_util.assert_list(expected, actual)


@Then(u"{webapp_user}成功获取'{product_name}'的商品详情的'更多评价'")
def step_impl(context, webapp_user, product_name):
	"""
	@see 原Webapp的`webapp_product_review_steps.py`
	"""
	product = bdd_util.get_product_by(product_name)
	expected = json.loads(context.text)
	#url = "/workbench/jqm/preview/?woid=%d&module=mall&model=product&rid=%d" % (context.webapp_owner_id, product.id)
	url = "/mall/product_reviews/"
	#response = context.client.get(bdd_util.nginx(url), follow=True)
	response = context.client.get(url, {
			'woid': context.webapp_owner_id,
			'product_id': product.id
		})
	bdd_util.assert_api_call_success(response)	

	data = response.data
	logging.debug('response.data: {}'.format(data))
	product_review_list = data['reviews']
	actual = []
	if product_review_list:
		for i in product_review_list:
			data = {}
			#data['member'] = i.member_name
			member = bdd_util.get_member_by_id(i['member_id'])
			data['member'] = member.username
			data['review_detail'] = i['review_detail']
			actual.append(data)
	else:
		actual.append({})
	bdd_util.assert_list(expected, actual)


@When(u"{webapp_user}在商城首页点击'{product_name}'的链接")
def step_click_product(context, webapp_user, product_name):
	pass


@When(u"{webapp_user}在'{product_name}'的商品详情页点击'更多评价'")
def step_click_more(context, webapp_user, product_name):
	pass

@Given(u"{webapp_owner}已创建微众卡")
def step_impl(context, webapp_owner):
	"""
	输入示例：
	```
	{
		"cards":[{
			"id":"0000001",
			"password":"1234567",
			"status":"未激活",
			"price":5.00
		},{
			"id":"0000002",
			"password":"1231231",
			"status":"已过期",
			"price":5.00
		}]
	}	
	```
	@see `weapp/features/steps/market_tools_weizoom_card_steps.py` 
	"""
	data = json.loads(context.text)
	url = "/wzcard/wzcard/"
	success = 0
	for card in data['cards']:
		# 创建1个微众卡
		response = context.client.put(url, {
				'woid': context.webapp_owner_id,
				'wzcard_id': card['id'],
				'status': card['status'],
				'balance': card['price']
			})
		bdd_util.assert_api_call_success(response)	
		success+=1
	context.tc.assertEquals(len(data['cards']), success)


@Then(u"{webapp_owner}能获取微众卡'{wzcard_id}'")
def step_impl(context, webapp_owner, wzcard_id):
	expected = json.loads(context.text)
	expected['price'] = float(expected['price'])
	url = "/wzcard/wzcard/"
	response = context.client.get(url, {
			'woid': context.webapp_owner_id,
			'wzcard_id': wzcard_id
		})
	bdd_util.assert_api_call_success(response)

	real = {
		'status': response.data['readable_status'],
		'price': float(response.data['balance'])
	}
	bdd_util.assert_dict(expected, real)


@When(u'{webapp_user}进行微众卡余额查询')
def step_impl(context, webapp_user):
	args = json.loads(context.text)
	context.wzcard_info = {
		'id': args['id'],
		'password': args['password']
	}


@Then(u'{webapp_user}获得微众卡余额查询结果')
def step_impl(context, webapp_user):
	wzcard_id = context.wzcard_info['id']
	wzcard_password = context.wzcard_info['password']

	url = "/wzcard/usable_wzcard/"
	response = context.client.get(url, {
			'woid': context.webapp_owner_id,
			'wzcard_id': wzcard_id,
			'password': wzcard_password,
		})
	bdd_util.assert_api_call_success(response)

	logging.info('response.data: {}'.format(response.data))
	context.tc.assertEquals(200, response.data['code'])

	real = {
		#'status': response.data['readable_status'],
		'card_remaining': float(response.data['balance'])
	}
	msg = response.data.get('msg')
	if msg:
		real['msg'] = msg

	expected = json.loads(context.text)
	bdd_util.assert_dict(expected, real)


@Then(u"{webapp_user}获得错误信息'{expected_msg}'")
def step_impl(context, webapp_user, expected_msg):
	wzcard_id = context.wzcard_info['id']
	wzcard_password = context.wzcard_info['password']

	url = "/wzcard/usable_wzcard/"
	response = context.client.get(url, {
			'woid': context.webapp_owner_id,
			'wzcard_id': wzcard_id,
			'password': wzcard_password,
		})
	bdd_util.assert_api_call_success(response)

	# TODO: 统一API返回代码
	context.tc.assertEquals(400, response.data['code'])

	logging.info('response.data: {}'.format(response.data))
	msg = response.data['msg']
	context.tc.assertEquals(expected_msg, msg)
