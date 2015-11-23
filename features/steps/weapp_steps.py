# -*- coding: utf-8 -*-
import json
import time
import shutil
import os
from datetime import datetime, timedelta
import subprocess

from behave import *
import requests

import settings

def _run_weapp_step(step, context):
	url = 'http://%s:%s' % (settings.WEAPP_BDD_SERVER_HOST, settings.WEAPP_BDD_SERVER_PORT)
	data = {
		'step': step,
		'context': context
	}
	requests.post(url, data={'data':json.dumps(data)})

@When(u"{command}:weapp")
def step_impl(context, command):
	_run_weapp_step(u'When %s' % command, context.text)

@Given(u"{command}:weapp")
def step_impl(context, command):
	_run_weapp_step(u'Given %s' % command, context.text)

@Then(u"{ignore}:weapp")
def step_impl(context, ignore):
	import sys
	print >> sys.stderr, u'ignore weapp operation: %s' % ignore

@When(u"执行weapp操作:skip")
def step_impl(context):
	pass

@when(u"重置weapp的bdd环境")
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
