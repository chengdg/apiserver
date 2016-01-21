# -*- coding: utf-8 -*-

import os
import sys
import logging

from db.mall import models as mall_models

path = os.path.abspath(os.path.join('.', '..'))
sys.path.insert(0, path)

import unittest
from pymongo import Connection

import settings
from features.util import bdd_util
from core.cache import utils as cache_utils
from core.service import celeryconfig

######################################################################################
# __clear_all_account_data: 清空账号数据
######################################################################################
def __clear_all_account_data():
	pass


######################################################################################
# __clear_all_app_data: 清空应用数据
######################################################################################
def __clear_all_app_data():
	pass

######################################################################################
# __create_system_user: 创建系统用户
######################################################################################
def __create_system_user(username):
	pass


def before_all(context):
	cache_utils.clear_db()
	# __clear_all_account_data()
	# __create_system_user('jobs')
	# __create_system_user('bill')
	# __create_system_user('tom')

	weapp_working_dir = os.path.join(settings.WEAPP_DIR, 'weapp')
	if not os.path.exists(weapp_working_dir):
		info = '* ERROR: CAN NOT do bdd testing. Because bdd need %s be exists!!!' % weapp_working_dir
		info = info.replace(os.path.sep, '/')
		print('*' * 80)
		print(info)
		print('*' * 80)
		sys.exit(3)

	#创建test case，使用assert
	context.tc = unittest.TestCase('__init__')
	bdd_util.tc = context.tc

	#设置bdd模式
	settings.IS_UNDER_BDD = True

	#启动weapp下的bdd server
	#print u'TODO2: 启动weapp下的bdd server'
	logging.warning(u'TODO2: 启动weapp下的bdd server')

	#登录添加App
	#client = bdd_util.login('manager')

	# 让Celery以同步方式运行
	celeryconfig.CELERY_ALWAYS_EAGER = True



def after_all(context):
	pass


def before_scenario(context, scenario):
	is_ui_test = False
	context.scenario = scenario
	for tag in scenario.tags:
		if tag.startswith('ui-') or tag == 'ui':
			is_ui_test = True
			break

	if is_ui_test:
		#创建浏览器
		print('[before scenario]: init browser driver')
		chrome_options = Options()
		chrome_options.add_argument("--disable-extensions")
		chrome_options.add_argument("--disable-plugins")
		driver = webdriver.Chrome(chrome_options=chrome_options)
		driver.implicitly_wait(3)
		context.driver = driver

	__clear_all_app_data()


def after_scenario(context, scenario):
	if hasattr(context, 'client') and context.client:
		context.client.logout()

	if hasattr(context, 'driver') and context.driver:
		print('[after scenario]: close browser driver')
		page_frame = PageFrame(context.driver)
		page_frame.logout()
		context.driver.quit()

	if hasattr(context, 'webapp_driver') and context.driver:
		print('[after scenario]: close webapp browser driver')
		context.webapp_driver.quit()

