# -*- coding: utf-8 -*-
#import json
from hashlib import md5

from behave import *
from db.mall.models import *
from features.util import bdd_util
#from features.util.helper import WAIT_SHORT_TIME
from db.account import models as account_models
from db.mall import models as mall_models
from db.member import models as member_models

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

from bddserver import call_bdd_server_steps
from features.util import http

def __create_member(username, mp_user_name):
	webapp_owner = account_models.User.select().dj_where(username=mp_user_name).get()
	profile = account_models.UserProfile.select().dj_where(user=webapp_owner).get()

	webapp_id = profile.webapp_id
	if member_models.SocialAccount.select().dj_where(webapp_id=webapp_id).count() == 0:
		#创建SocialAccount
		openid = '%s_%s' % (username, mp_user_name)
		token = md5(openid).hexdigest()
		social_account = member_models.SocialAccount.create(
			webapp_id = webapp_id,
			openid = openid,
			token = token,
			platform = member_models.SOCIAL_PLATFORM_WEIXIN,
			is_for_test = False
		)

		#创建member
		from util.string_util import byte_to_hex
		member_grade = member_models.MemberGrade.select().dj_where(webapp_id=webapp_id).get()
		member = member_models.Member.create(
            webapp_id = webapp_id,
            token = token,
            grade = member_grade,
            integral = 0,
            is_subscribed = True,
            status = 1,
            username_hexstr = byte_to_hex(username)
        )

        #创建WebappUser
        webapp_user = member_models.WebAppUser.create(
        	webapp_id = webapp_id,
        	token = token,
        	member_id = member.id
        )

        #创建MemberHasSocialAccount
        member_models.MemberHasSocialAccount.create(
        	webapp_id = webapp_id,
        	member = member,
        	account = social_account
        )

@when(u"{user}关注{mp_user_name}的公众号")
def step_impl(context, user, mp_user_name):
	#call_bdd_server_steps._run_bdd_server_step(u'When %s关注%s的公众号' % (user, mp_user_name), context, u'weapp')
	__create_member(user, mp_user_name)

@given(u"{user}关注{mp_user_name}的公众号")
def step_impl(context, user, mp_user_name):
	#call_bdd_server_steps._run_bdd_server_step(u'Given %s关注%s的公众号' % (user, mp_user_name), context, u'weapp')
	__create_member(user, mp_user_name)

@when(u"{user}访问{mp_user_name}的webapp")
def step_impl(context, user, mp_user_name):
	webapp_owner = account_models.User.get(username=mp_user_name)
	profile = account_models.UserProfile.get(user=webapp_owner.id)
	client = bdd_util.login(user)

	#access_token = account_models.AccessToken.get(openid=openid).access_token
	
	#获得访问mp_user_name数据的access token
	#修改授权方式
	#换取code
	# url = "http://api.weapp.com/member_service/oauth/oauth/?_method=post"
	# data = {
	# 	'woid': webapp_owner.id,
	# 	'openid': '%s_%s' % (user, mp_user_name)
	# }
	# result = http.request(url, data, 'post')

	# code = result['data']['code']
	
	# #get accesstoken
	# url = "http://api.weapp.com/member_service/oauth/access_token/?_method=post"
	# data = {
	# 	'woid': webapp_owner.id,
	# 	'code': code
	# }
	# result = http.request(url, data, 'post')
	# openid = '%s_%s' % (user, mp_user_name)
	# client.webapp_user.access_token = result['data']['access_token']
	# logging.info('>>>>>> ACCESS_TOKEN : %s' % client.webapp_user.access_token)
	# client.woid = webapp_owner.id

	openid = '%s_%s' % (user, mp_user_name)
	access_token = account_models.AccessToken.create(
		access_token = openid,
		woid = webapp_owner.id,
		openid = openid,
		expires_in = ''
	)

	client.webapp_user.access_token = access_token.access_token
	context.webapp_owner_id = webapp_owner.id
	context.webapp_owner = webapp_owner
	context.webapp_id = profile.webapp_id

	logging.info(">>>>>>>>>>>>>>:::@@#@:")
	logging.info(client.webapp_user.access_token)
	logging.info(">>>>>>>>>>>>>>:::@@#@:2")
	#获取数据库中的webapp_user
	member = bdd_util.get_member_for(user, context.webapp_id)
	db_webapp_user = member_models.WebAppUser.get(member_id=member.id)
	client.webapp_user.id = db_webapp_user.id
	context.client = client
	context.webapp_user = client.webapp_user


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