# -*- coding: utf-8 -*-
import json
import time

from behave import *

from db.mall.promotion_models import COUPONSTATUS
from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
from db.mall import models as mall_models
from db.member import models as member_models

from business.account.webapp_user import WebAppUser
from business.account.webapp_owner import WebAppOwner

from eaglet.core.cache import utils as cache_util
import logging

@when(u"{webapp_user_name}获取手机绑定验证码'{phone_number}'")
def step_impl(context, webapp_user_name, phone_number):
	webapp_owner_id = context.webapp_owner_id
	response = context.client.get('/wapi/member/member_phone_captcha/', {
		'phone_number':phone_number,
		'sessionid':'session_id'
	})
	##
	actual = response.body['data']['captcha']


	# expected = int(integral_count)
	context.tc.assertEquals(4, len(actual))
	context.captcha = actual


@when(u"{webapp_user_name}使用验证码绑定手机")
def step_impl(context, webapp_user_name):
	expected = json.loads(context.text)
	
	captcha = ''
	if expected.has_key('verification_code'):
		captcha = expected['verification_code']
	else:
		if hasattr(context , 'captcha'):
			captcha = context.captcha
	phone_number = expected['phone']

	response = context.client.put('/wapi/member/member_binding_phone/', {
		'phone_number':phone_number,
		'sessionid':'session_id',
		'captcha': captcha
	})

@then(u"{webapp_user_name}获得个人中心手机绑定信息")
def step_impl(context, webapp_user_name):
	webapp_owner_id = context.webapp_owner_id
	response = context.client.get('/wapi/user_center/user_center/', {
	})
	
	expected = json.loads(context.text)
	actual = response.body['data']['phone']

	context.tc.assertEquals(expected['phone'], actual)

