# -*- coding: utf-8 -*-
import json

from behave import *

from features.util import bdd_util
from features.util.behave_utils import get_context_attrs


@then(u"apiserver获得context")
def step_impl(context):
	"""
	@type context: behave.runner.Context
	"""
	expected = json.loads(context.text)
	actual = get_context_attrs(context)
	bdd_util.assert_dict(expected, actual)


