# -*- coding: utf-8 -*-
import base64
import os
import subprocess

import requests
from behave import *

# from django.contrib.auth.models import User

from db.mall.models import *
from features.util.behave_utils import get_context_attrs


def _run_weapp_step(step, context_text,context=None):
	url = 'http://%s:%s' % (settings.WEAPP_BDD_SERVER_HOST, settings.WEAPP_BDD_SERVER_PORT)
	if context:
		context_kvs = get_context_attrs(context)
	else:
		context_kvs = {}
	data = {
		'step': step,
		'context_text': context_text,
		'context_kvs': json.dumps(context_kvs)
	}
	response = requests.post(url, data={'data':json.dumps(data)})

	response_text = base64.b64decode(response.text.encode('utf-8')).decode('utf-8')
	if response_text.startswith('***'):
		buf = []
		buf.append('\n*************** START WEAPP STEP EXCEPTION ***************')
		buf.append(response_text.strip())
		buf.append('*************** FINISH WEAPP STEP EXCEPTION ***************\n')
		print '\n'.join(buf)
		assert False, 'weapp_step_response.text != "success", Weapp step has EXCEPTION!!!'
	else:
		try:
			context_kvs = json.loads(response_text)
			for k,v in context_kvs.items():
				setattr(context,k,v)
		except BaseException as e:
			pass

@When(u"{command}:weapp")
def step_impl(context, command):
	_run_weapp_step(u'When %s' % command, context.text, context)

@Given(u"{command}:weapp")
def step_impl(context, command):
	_run_weapp_step(u'Given %s' % command, context.text, context)


@Then(u"{command}:weapp")
def step_impl(context, command):
	_run_weapp_step(u'Then %s' % command, context.text, context)

# @Then(u"{ignore}:weapp")
# def step_impl(context, ignore):
# 	import sys
# 	print >> sys.stderr, u'ignore weapp operation: %s' % ignore

@When(u"执行weapp操作:skip")
def step_impl(context):
	pass

@given(u"重置weapp的bdd环境")
def step_impl(context):
	_run_weapp_step('__reset__', None)

@When(u"执行weapp操作")
def step_impl(context):
	buf = [
		'\n',
		'*' * 80,
		'*** start run weapp steps',
		'*' * 80
	]
	print '\n'.join(buf)
	scenario_name = context.scenario.name.encode('utf-8')

	src = open(context.scenario.filename, 'rb')
	lines = []
	for line in src:
		if ('Scenario:' in line) and (scenario_name in line):
			prev_line = lines[-1]
			if '@' in prev_line:
				lines[-1] = '%s @apiserver_wip' % prev_line 
			else:
				lines.append('@apiserver_wip')

		lower_line = line.lower()
		#为非weapp指令添加':wglass'，以阻止weapp执行指令
		if ('when ' in lower_line) or ('given ' in lower_line) or ('then ' in lower_line):
			if not ':weapp' in lower_line:
				line = '%s:wglass' % line.rstrip()

		lines.append(line.rstrip())
	content = '\n'.join(lines).replace(':weapp', '')
	src.close()

	weapp_feature_file_path = os.path.join(settings.WEAPP_DIR, 'weapp/features/apiserver.feature')
	dst = open(weapp_feature_file_path, 'wb')
	print >> dst, content
	dst.close()

	current_dir = os.getcwd()
	weapp_working_dir = os.path.join(settings.WEAPP_DIR, 'weapp')
	os.chdir(weapp_working_dir)
	results = subprocess.check_output("behave -k --no-capture -t @apiserver_wip", shell=True)
	buf = [
		'>' * 60,
		results,
		'>' * 60,
		'*' * 80,
		'*** finish run weapp steps',
		'*' * 80,
		'\n'
	]
	print '\n'.join(buf)
	os.chdir(current_dir)
	#results = subprocess.check_output("pwd", shell=True)


@when(u"{webapp_user_name}把{webapp_owner_name}的'{product_name_one}'链接的商品ID修改成{webapp_owner_name_other}的'{product_name_two}'的商品ID")
def step_impl(context, webapp_user_name, webapp_owner_name, product_name_one,webapp_owner_name_other,product_name_two):
	user_other = User.get(User.username==webapp_owner_name_other).id
	product_two = Product.select().dj_where(owner_id=user_other,name=product_name_two).get()
	url = '/wapi/mall/product/?woid=%s&product_id=%d' % (context.webapp_owner_id, product_two.id)
	context.url = url

@when(u"{webapp_user_name}访问修改后的链接")
def step_impl(context, webapp_user_name):
	context.response = context.client.get(context.url)

@then(u"{webapp_user_name}获得商品不存在提示")
def step_impl(context,webapp_user_name):
	product = context.response.data
	if product['is_deleted']:
		return True
	else:
		return False
