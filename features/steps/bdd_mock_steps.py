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
    print('----------------ffff',bdd_mock)
    expected = json.loads(context.text)
    actual = bdd_util.get_bdd_mock('template_message')
    bdd_util.assert_dict(expected, actual)
