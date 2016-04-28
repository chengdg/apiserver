# -*- coding: utf-8 -*-
import json
import db.mall.models as mall_models
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

@then(u'server能获取alipay_interface接口信息')
def step_impl(context):
    expected = json.loads(context.text)
    order_id = expected['order_id']
    url = '/pay/alipay_interface/?order_id=%s' % (order_id)
    actual = context.client.get(bdd_util.nginx(url), follow=True).data
    bdd_util.assert_dict(expected, actual)

@then(u'server能获取wxpay_interface接口信息')
def step_impl(context):
    expected = json.loads(context.text)
    order_id = expected['order_id']
    url = '/pay/wxpay_interface/?order_id=%s' % (order_id)
    actual = context.client.get(bdd_util.nginx(url), follow=True).data
    actual['pay_interface_type'] = '微信支付'
    actual['pay_version'] = 'v2' if actual['pay_version'] == mall_models.V2 else 'v3'
    actual['order_id'] = order_id
    bdd_util.assert_dict(expected, actual)

@then(u'server能获取wxpay_package接口信息')
def step_impl(context):
    expected = json.loads(context.text)
    order_id = expected['order_id']
    url = '/pay/wxpay_package/?order_id=%s&config=0' % (order_id)
    actual = context.client.get(bdd_util.nginx(url), follow=True).data
    actual['order_id'] = order_id
    bdd_util.assert_dict(expected, actual)