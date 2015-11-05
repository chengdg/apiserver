# -*- coding: utf-8 -*-
import json

from behave import *

from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
from wapi.user import models as user_models

@given(u"{user}获得访问'{webapp_owner_name}'数据的授权")
def step_impl(context, user, webapp_owner_name):
	#进行登录，并获取context.client.user, context.client.woid
	bdd_util.login(user, None, context=context)

	webapp_owner = user_models.User.get(user_models.User.username==webapp_owner_name)
	context.client.woid = webapp_owner.id
	print(context.client.woid)


@then(u"{user}获得错误提示'{error}'")
def step_impl(context, user, error):
	context.tc.assertEquals(error, context.server_error_msg)

@then(u"{user}获得'{product_name}'错误提示'{error}'")
def step_impl(context, user, product_name ,error):
	detail = context.response_json['data']['detail']
	context.tc.assertEquals(error, detail[0]['short_msg'])
	pro_id = ProductFactory(name=product_name).id
	context.tc.assertEquals(pro_id, detail[0]['id'])