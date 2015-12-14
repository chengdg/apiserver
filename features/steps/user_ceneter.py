# -*- coding: utf-8 -*-
import json
import time

from behave import *

from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
from db.mall import models as mall_models
from db.member import models as member_models

from business.account.webapp_user import WebAppUser
from business.account.webapp_owner import WebAppOwner

from core.cache import utils as cache_util
import logging

@then(u"{webapp_user_name}在{webapp_owner_name}的webapp中拥有{integral_count}会员积分")
def step_impl(context, webapp_user_name, webapp_owner_name, integral_count):
	webapp_owner_id = context.webapp_owner_id
	response = context.client.get('/wapi/user_center/user_center/', {
	})
	
	##expected = json.loads(context.text)
	actual = response.body['data']['integral']

	expected = int(integral_count)
	context.tc.assertEquals(expected, actual)


@when(u"{webapp_user_name}获得{webapp_owner_name}的{integral_count}会员积分")
def step_impl(context, webapp_user_name, webapp_owner_name, integral_count):
	webapp_owner_id = context.webapp_owner_id
	webapp_id = bdd_util.get_webapp_id_for(webapp_owner_name)
	member = bdd_util.get_member_for(webapp_user_name, webapp_id)
	member_models.Member.update(integral=int(integral_count)).dj_where(id=member.id).execute()

	webapp_owner = WebAppOwner.get({
			'woid': webapp_owner_id
		})

	webapp_user = WebAppUser.from_member_id({
		'webapp_owner': webapp_owner,
		'member_id': member.id
		})
	webapp_user.cleanup_cache()
