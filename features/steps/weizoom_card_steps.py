# -*- coding: utf-8 -*-
import base64
import json
import requests
from behave import *
import settings


from features.util.behave_utils import get_context_attrs


def _run_weizoom_card_step(step, context_text, context=None):
	url = 'http://%s:%s' % (settings.WEIZOOM_CARD_BDD_SERVER_HOST, settings.WEIZOOM_CARD_BDD_SERVER_PORT)
	if context:
		context_kvs = get_context_attrs(context)
	else:
		context_kvs = {}
	data = {
		'step': step,
		'context_text': context_text,
		'context_kvs': json.dumps(context_kvs)
	}
	response = requests.post(url, data={'data': json.dumps(data)})

	response_text = base64.b64decode(response.text.encode('utf-8')).decode('utf-8')
	# 可以有更好的判断条件。。。
	if response_text.startswith('Traceback'):
		buf = []
		buf.append('\n*************** START WEAPP STEP EXCEPTION ***************')
		buf.append(response_text.strip())
		buf.append('*************** FINISH WEAPP STEP EXCEPTION ***************\n')
		print '\n'.join(buf)
		assert False, 'weizoom_card_step_response.text != "success", Weapp step has EXCEPTION!!!'
	else:
		try:
			context_kvs = json.loads(response_text)
			for k, v in context_kvs.items():
				setattr(context, k, v)
		except BaseException as e:
			pass


@When(u"{command}:weizoom_card")
def step_impl(context, command):
	_run_weizoom_card_step(u'When %s' % command, context.text, context)


@Given(u"{command}:weizoom_card")
def step_impl(context, command):
	_run_weizoom_card_step(u'Given %s' % command, context.text, context)


@Then(u"{command}:weizoom_card")
def step_impl(context, command):
	_run_weizoom_card_step(u'Then %s' % command, context.text, context)

@given(u"重置weizoom_card的bdd环境")
def step_impl(context):
	_run_weizoom_card_step('__reset__', None)