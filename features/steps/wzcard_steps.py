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


@when(u"{user}绑定微众卡")
def step_impl(context, user):
	"""
	@type context: behave.runner.Context
	"""
	_a = json.loads(context.text)['weizoom_card_info']

	url = '/wzcard/order/?_method=put'
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
		actual = json.loads(context.text)
		code = actual['code']
		data = actual['data']
		type = data['type']

		if msg == u'恭喜您 绑定成功':
			assert code == 200
		else:
			assert code == 500
			if msg == u'卡号或密码错误':
				assert type in ('wzcard:nosuch', 'wzcard:wrongpass')
			elif msg == u'该微众卡余额为0！':
				assert type in ('wzcard:exhausted')
			elif msg == u'该微众卡已经添加！':
				assert type in ('wzcard:has_bound')
			elif msg == u'微众卡未激活！':
				assert type in ('wzcard:inactive')
			elif msg == u'微众卡已过期！':
				assert type in ('wzcard:expired')
			elif msg == u'该专属卡不能在此商家使用！':
				assert type in ('wzcard:banned')

			else:
				raise NotImplementedError
