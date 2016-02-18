# -*- coding: utf-8 -*-
import json

from features.util import bdd_util
from behave import *

from features.util.bdd_util import bdd_mock


@then(u"server能发送邮件")
def step_impl(context):
    expected = json.loads(context.text)
    actual = bdd_util.get_bdd_mock('notify_mail')
    bdd_util.assert_dict(expected, actual)

@then(u'server能发送模板消息')
def step_impl(context):
    expected = json.loads(context.text)
    actual = bdd_util.get_bdd_mock('template_message')
    bdd_util.assert_dict(expected, actual)

@then(u'server能获得alipay_interface接口信息')
def step_impl(context):
    expected = json.loads(context.text)
    order_id = expected['order_id']
    url = '/wapi/pay/alipay_interface/?order_id=%s' % (order_id)
    actual = context.client.get(bdd_util.nginx(url), follow=True).data
    bdd_util.assert_dict(expected, actual)