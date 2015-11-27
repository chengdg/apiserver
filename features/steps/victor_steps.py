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
			context.execute_steps(u'When %s访问%s的webapp'% (buyer, web_user))
			last_buyer = buyer

		products = order['products']
		new_step = u'''When %s购买%s的商品
			"""
			{
				"products": %s
			}
			"""
		''' % (buyer, web_user, json.dumps(products))
		logging.info("Converted step:\n %s" % new_step)
		context.execute_steps(new_step)
	return
