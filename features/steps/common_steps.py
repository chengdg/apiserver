# -*- coding: utf-8 -*-
#import json

from behave import *
from db.mall.models import *
from features.util import bdd_util
#from features.util.helper import WAIT_SHORT_TIME
from db.account import models as account_models
from db.mall import models as mall_models
from db.member import models as member_models

from features.steps import call_bdd_server_steps
import logging

# @given(u"{user}获得访问'{webapp_owner_name}'数据的授权")
# def step_impl(context, user, webapp_owner_name):
# 	#进行登录，并获取context.client.user, context.client.woid
# 	weapp_steps._run_weapp_step(u'When %s关注%s的公众号' % (user, webapp_owner_name), None)
# 	weapp_steps._run_weapp_step(u'When %s访问%s的webapp' % (user, webapp_owner_name), None)

# 	bdd_util.login(user, None, context=context)

# 	webapp_owner = account_models.User.get(username=webapp_owner_name)
# 	user = account_models.User.get(username=user)
# 	profile = account_models.UserProfile.get(user=user.id)

# 	context.client.woid = webapp_owner.id
# 	context.webapp_owner_id = weapp_owner.id
# 	context.webapp_user = user
# 	context.webapp_id = profile.webapp_id
	

@then(u"{user}获得错误提示'{error}'")
def step_impl(context, user, error):
	context.tc.assertTrue(200 != context.response.body['code'])
	
	data = context.response.data
	server_error_msg = data.get('msg', None)
	if not server_error_msg:
		server_error_msg = data['detail'][0]['msg']

	context.tc.assertEquals(error, server_error_msg)

@then(u"{user}获得'{product_name}'错误提示'{error}'")
def step_impl(context, user, product_name ,error):
	context.tc.assertTrue(200 != context.response.body['code'])
	
	data = context.response.data
	detail = data['detail']
	context.tc.assertEquals(error, detail[0]['short_msg'])
	expected_product_id = mall_models.Product.get(name=product_name).id
	context.tc.assertEquals(expected_product_id, detail[0]['id'])

# @when(u"{user}关注{mp_user_name}的公众号")
# def step_impl(context, user, mp_user_name):
# 	weapp_steps._run_weapp_step(u'When %s关注%s的公众号' % (user, mp_user_name), None)
#
# @given(u"{user}关注{mp_user_name}的公众号")
# def step_impl(context, user, mp_user_name):
# 	weapp_steps._run_weapp_step(u'Given %s关注%s的公众号' % (user, mp_user_name), None)
#
# @when(u"{user}访问{mp_user_name}的webapp")
# def step_impl(context, user, mp_user_name):
# 	weapp_steps._run_weapp_step(u'When %s访问%s的webapp' % (user, mp_user_name), None)

from bddserver.files import call_bdd_server_steps

@when(u"{user}关注{mp_user_name}的公众号")
def step_impl(context, user, mp_user_name):
	call_bdd_server_steps._run_bdd_server_step(u'When %s关注%s的公众号' % (user, mp_user_name), context, u'weapp')

@given(u"{user}关注{mp_user_name}的公众号")
def step_impl(context, user, mp_user_name):
	call_bdd_server_steps._run_bdd_server_step(u'Given %s关注%s的公众号' % (user, mp_user_name), context, u'weapp')

@when(u"{user}访问{mp_user_name}的webapp")
def step_impl(context, user, mp_user_name):
	call_bdd_server_steps._run_bdd_server_step(u'When %s访问%s的webapp' % (user, mp_user_name), context, u'weapp')


	# from eaglet.core.db import models as db_models
	# db_models.db.close()
	#db_models.db.connect()

	webapp_owner = account_models.User.get(username=mp_user_name)
	profile = account_models.UserProfile.get(user=webapp_owner.id)
	client = bdd_util.login(user, None, context=context)
	
	#获得访问mp_user_name数据的access token
	response = client.put('/user/access_token/', {
		'woid': webapp_owner.id,
		'openid': '%s_%s' % (user, mp_user_name)
	})
	client.webapp_user.access_token = response.body['data']['access_token']
	logging.info('>>>>>> ACCESS_TOKEN : %s' % client.webapp_user.access_token)
	client.woid = webapp_owner.id

	context.webapp_owner_id = webapp_owner.id
	context.webapp_owner = webapp_owner
	context.webapp_id = profile.webapp_id

	#获取数据库中的webapp_user
	member = bdd_util.get_member_for(user, context.webapp_id)
	db_webapp_user = member_models.WebAppUser.get(member_id=member.id)
	client.webapp_user.id = db_webapp_user.id
	context.webapp_user = client.webapp_user
	if hasattr(context, 'fmt'):
		if hasattr(context, 'o_fmt') and context.o_fmt:
			pass
		else:
			context.o_fmt = context.fmt
			context.o_shared_url = context.shared_url

	context.fmt = ''
	context.shared_url = ''


@when(u"{webapp_user_name}把{webapp_owner_name}的'{product_name_one}'链接的商品ID修改成{webapp_owner_name_other}的'{product_name_two}'的商品ID")
def step_impl(context, webapp_user_name, webapp_owner_name, product_name_one,webapp_owner_name_other,product_name_two):
	user_other = User.get(User.username==webapp_owner_name_other).id
	product_two = Product.select().dj_where(owner_id=user_other,name=product_name_two).get()
	url = '/mall/product/?woid=%s&product_id=%d' % (context.webapp_owner_id, product_two.id)
	context.url = url

@when(u"{webapp_user_name}访问修改后的链接")
def step_impl(context, webapp_user_name):
	context.response = context.client.get(context.url)

@then(u"{webapp_user_name}获得商品不存在提示")
def step_impl(context,webapp_user_name):
	product = context.response.data
	if product['is_deleted']:
		return True
	else:
		return False