# -*- coding: utf-8 -*-
import json

from features.util import bdd_util
from behave import *


@then(u"server能发送邮件")
def step_impl(context):
    expected = json.loads(context.text)
    actual = bdd_util.get_bdd_mock('notify_mail')
    print('----------e', expected)
    print('----------a', actual)
    bdd_util.assert_dict(expected, actual)
