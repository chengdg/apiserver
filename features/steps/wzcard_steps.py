# -*- coding: utf-8 -*-
import json
import time

from behave import *

from db.mall.promotion_models import COUPONSTATUS
from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
from db.mall import models as mall_models
from db.member import models as member_models
from db.wzcard import models as wzcard_models

from business.account.webapp_user import WebAppUser
from business.account.webapp_owner import WebAppOwner

from eaglet.core.cache import utils as cache_util
import logging
import datetime
SOURCE2TEXT = {
	wzcard_models.WEIZOOM_CARD_SOURCE_REBATE: u'返利活动',
	wzcard_models.WEIZOOM_CARD_SOURCE_VIRTUAL: u'福利卡券',
	wzcard_models.WEIZOOM_CARD_SOURCE_BIND: u'绑定卡',
}

STATUS2TEXT = {
	'inactive': u'未激活',
	'empty': u'已用完'
}


@when(u"{user}绑定微众卡")
def step_impl(context, user):
	"""
	@type context: behave.runner.Context
	"""
	_a = json.loads(context.text)['weizoom_card_info']

	url = '/wzcard/binding_card/?_method=put'
	data = {
		'card_number': _a['id'],
		'card_password': _a['password']
	}
	context.response = context.client.post(url, data)

@then(u"{user}获得绑定微众卡提示信息'{msg}'")
def step_impl(context, user, msg):
	"""
	@type context: behave.runner.Context
	"""
	actual = context.response.body
	code = actual['code']
	data = actual['data']
	type = data.get('type')
	valid_time_to = data.get('valid_time_to')

	if msg == u'恭喜您 绑定成功':
		assert code == 200
	else:
		assert code == 500
		if msg == u'卡号或密码错误！':
			assert type in ('wzcard:nosuch', 'wzcard:wrongpass')
		elif msg == u'该微众卡余额为0！':
			assert type in ('wzcard:exhausted')
		elif msg == u'该微众卡已经添加！':
			assert type in ('wzcard:has_bound')
		elif msg == u'微众卡未激活！':
			assert type in ('wzcard:inactive')
		# elif msg == u'微众卡已过期！':
		# 	assert type in ('wzcard:expired')
		elif msg.endswith('过期'):
			assert type in ('wzcard:expired')

			valid_time_to = datetime.datetime.strptime(valid_time_to.split(' ')[0],'%Y-%m-%d')
			_msg = '该卡已于{}年{}月{}日过期'.format(valid_time_to.year, str(valid_time_to.month).zfill(2), valid_time_to.day)
			assert _msg==msg,'e:{},a:{}'.format(msg,_msg)

		elif msg == u'该专属卡不能在此商家使用！':
			assert type in ('wzcard:banned')

		else:
			raise NotImplementedError


@then(u"{user}获得微众卡包列表")
def step_impl(context, user):
	"""
	@type context: behave.runner.Context
	"""
	url = '/wzcard/binding_cards/'
	response = context.client.get(url)

	resp = response.body

	actual = resp['data']

	expected = json.loads(context.text)

	if 'usable_cards' in expected:
		for a in expected['usable_cards']:
			del a['actions']
			del a['binding_date']
	if 'unusable_cards' in expected:
		for a in expected['unusable_cards']:
			del a['actions']
			del a['binding_date']

	for a in actual['usable_cards']:
		a['source'] = SOURCE2TEXT[a['source']]
		a['valid_time_to'] = a['valid_time_to'][:16]
		a['valid_time_from'] = a['valid_time_from'][:16]

	for a in actual['unusable_cards']:
		a['source'] = SOURCE2TEXT[a['source']]
		a['valid_time_to'] = a['valid_time_to'][:16]
		a['valid_time_from'] = a['valid_time_from'][:16]
		a['status'] = STATUS2TEXT[a['status']]

	bdd_util.assert_dict(expected, actual)


@then(u"{user}能获得微众卡'{card_num}'的详情信息")
def step_impl(context, user, card_num):
	"""
	"""
	url = '/wzcard/detail/?_method=get'
	response = context.client.get(url,{'card_num':card_num})

	resp = response.body
	logging.error("zcard#######>>>>>>>2>>>>%s" % resp)
	actual = resp['data']['weizoom_card']

	actual_dict ={}

	actual_dict['id'] = actual['card_number']
	actual_dict['password'] = actual['card_password']
	actual_dict['card_end_date'] = actual['valid_time_to'].split(" ")[0]
	actual_dict['card_remain_value'] = float(actual['balance'])
	actual_dict['use_details'] =  actual['use_details']
	for actual_order_item in actual_dict['use_details']:
		actual_order_item['detail'] = -float(actual_order_item['money'])
		actual_order_item['order_info'] = "{},{}".format(actual_order_item['nickname'],actual_order_item['order_id'])


	expected = json.loads(context.text)
	expected['card_remain_value'] = float(expected['card_remain_value'])
	if expected.has_key('use_details'):
		for use_item in expected['use_details']:
			use_item.pop("time")
			use_item["detail"] = float(use_item["detail"])

	bdd_util.assert_dict(expected, actual_dict)

