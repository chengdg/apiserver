# -*- coding: utf-8 -*-
import json
import time

from behave import *

from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
from db.mall import models as mall_models
from db.member import models as member_models
from business.account.webapp_owner import WebAppOwner
from business.account.system_account import SystemAccount
from business.spread.member_spread import MemberSpread
import logging


def __get_member_by_openid(openid):
	try:
		social_account = member_models.SocialAccount.get(openid=openid)
		member = member_models.MemberHasSocialAccount.get(account=social_account).member
		return member
	except:
		return None

@When(u'{user}分享{shared_user}分享{webapp_owner_name}的微站链接到朋友圈')
def step_impl(context, user, shared_user, webapp_owner_name):
	openid = '%s_%s' % (user, webapp_owner_name)
	member = __get_member_by_openid(openid)
	context.fmt = member.token
	shared_url = u'/mall/product/?fmt=%s' % (member.token)
	context.shared_url = shared_url
	# if member:
	# 	fmt = member.token
	# 	webapp_owner_id = bdd_util.get_user_id_for(webapp_owner_name)
	# 	url = '/workbench/jqm/preview/?module=mall&model=products&action=list&category_id=0&workspace_id=mall&webapp_owner_id=%d&fmt=%s' % (webapp_owner_id, fmt)
	# 	context.shared_url = url


@When(u'{shared_url}把{webapp_owner_name}的商品"{product_name}"的链接分享到朋友圈')
def step_impl(context, shared_url, webapp_owner_name, product_name):
	openid = '%s_%s' % (shared_url, webapp_owner_name)
	member = __get_member_by_openid(openid)
	context.fmt = member.token
	context.webapp_owner_name = webapp_owner_name
	#context.shared_url = product_name
	shared_url = u'/mall/product/?fmt=%s&product_name=%s' % (member.token, product_name)


	context.shared_url = shared_url

	response = context.client.put('/wapi/member/shared_url/', {
		'title': product_name,
		'shared_url': shared_url
	})

	# if member:
	# 	fmt = member.token
	# 	webapp_owner_id = bdd_util.get_user_id_for(webapp_owner_name)
	# 	product_id = Product.objects.get(name=product_name).id
	# 	url = '/termite/workbench/jqm/preview/?module=mall&model=product&action=get&rid=%d&woid=%d&fmt=%s&from=timeline' % (product_id, webapp_owner_id, fmt)
	# 	context.shared_url = url

@When(u'{webapp_user_name}点击{shared_webapp_user_name}分享链接')
def step_impl(context, webapp_user_name, shared_webapp_user_name):
	webapp_owner_name = context.webapp_owner_name
	current_openid = '%s_%s' % (webapp_user_name, webapp_owner_name)
	current_member = __get_member_by_openid(current_openid)

	shared_openid = '%s_%s' % (shared_webapp_user_name, webapp_owner_name)
	shared_member = __get_member_by_openid(shared_openid)
	# logging.error('>>>>>>>>.aaaaaaaaaaaaaaaaaaa')
	# logging.error(shared_member.token)
	# logging.error('>>>>>>>bbbbbbbbbbbbbbbbbbbbbbb')
	if hasattr(context, 'shared_url') and context.shared_url:
		shared_url = context.shared_url
	else:	
		shared_url = context.o_shared_url
		context.shared_url = context.o_shared_url #'/mall/products/?fmt='+shared_member.token
		context.fmt = context.o_fmt

	if not current_member:
		webapp_owner_id = context.webapp_owner_id
		webapp_owner = WebAppOwner.get({
			'woid': webapp_owner_id
		})
		
		member_account = MemberSpread.process_openid_for({
			'openid': current_openid,
			'for_oauth':'1',
			'url': context.shared_url,
			'woid': webapp_owner.id,
			'webapp_owner': webapp_owner
			})


	new_step = u'''When %s访问%s的webapp'''% (webapp_user_name, webapp_owner_name)
	logging.info("Converted step:\n %s" % new_step)
	context.execute_steps(new_step)

	# logging.error('>>>>>>>>.aaaaaaaaaaaaaaaaaaa')
	# logging.error(shared_member.token)
	# logging.error('>>>>>>>bbbbbbbbbbbbbbbbbbbbbbb')

	context.fmt = shared_member.token
	context.shared_url = shared_url
	response = context.client.put('/wapi/member/member_spread/', {
		'fmt': shared_member.token,
		'url': context.shared_url
	})



@When('{user}通过{shared_user}分享的链接购买{webapp_owner_name}的商品')
def step_impl(context, user, shared_user, webapp_owner_name):
	context.execute_steps(u"when %点击%s分享链接" % (user, shared_user))
	context.execute_steps(u"when %s购买%s的商品" % (user, webapp_owner_name))


