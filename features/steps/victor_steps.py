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
	last_buyer = None
	for order in args:
		buyer = order['member']
		if buyer != last_buyer:
			# login first if not logged-in
			new_step = u'When %s访问%s的webapp'% (buyer, web_user)
			logging.info("Converted step:\n %s" % new_step)
			context.execute_steps(new_step)
			last_buyer = buyer

		products = order['products']
		order_id = order['order_no']
		new_step = u'''When %s购买%s的商品
			"""
			{
				"order_id": "%s",
				"products": %s
			}
			"""
		''' % (buyer, web_user, order_id, json.dumps(products))
		logging.info("Converted step:\n %s" % new_step)
		context.execute_steps(new_step)
		
	return

@When(u"{webapp_user}完成订单'{order_code}'中'{product_name}'的评价包括'{has_picture}'")
def step_finished_a_product_review(context, webapp_user, order_code, product_name, has_picture):
	"""
	完成订单评价

	@see 原Weapp中`features/steps/webapp_product_review_steps.py`
	"""
	context_dict = json.loads(context.text)

	url = '/wapi/mall/review/'
	#url = '/webapp/api/project_api/call/'
	# 原始源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
	"""
	NOTICE：这里有一个问题：下单流程中没有改写'order_id'，也就是说`order_id`是自然生成的，因此无法通过`oder_id=order_code`定位。需要用新的方式确定订单。
	"""
	order_has_product = bdd_util.get_order_has_product(order_code, product_name)
	params = {}
	params.update(context_dict)
	params.update({
		'woid': context.webapp_owner_id,
		'order_id': order_has_product.order_id,
		'product_id': order_has_product.product_id,
		'order_has_product_id': order_has_product.id,
		'_method': 'put',
	})
	# 输入
	#data['target_api'] = 'product_review/create'
	#data['module'] = 'mall'
	has_picture = context_dict.get('picture_list', None)
	if has_picture:
		params['picture_list'] = str(has_picture)

	context.client.post(url, params)
