# -*- coding: utf-8 -*-
"""@package business.mall.order_operation_log
订单操作日志

"""

import json
from bs4 import BeautifulSoup
import math
import itertools
import uuid
import time
import random
from datetime import datetime

from core.exceptionutil import unicode_full_stack
from core.watchdog.utils import watchdog_alert, watchdog_warning, watchdog_error

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
# import resource
from business import model as business_model 
import settings
from utils import regional_util

import logging

class OrderLogOperator(business_model.Model):
	"""订单操作日志
	"""
	__slots__ = (
	)

	@staticmethod
	def record_operation_log(order, operator, action):
		"""
		创建订单操作日志
		"""
		logging.info("to create an OrderOperationLog...")
		if order.origin_order_id > 0 and order.supplier > 0:  #add by duhao 如果是子订单，则加入供应商信息
			action = '%s - %s' % (action, mall_models.Supplier.get_supplier_name(order.supplier))

		order_operation_log, created = mall_models.OrderOperationLog.get_or_create(
			order_id=order.order_id,
			action=action,
			operator=operator
		)
		return order_operation_log


	@staticmethod
	def record_status_log(order, operator, from_status, to_status):
		"""
		创建订单状态日志
		"""
		logging.info("to create an OrderStatusLog...")
		order_status_log, created = mall_models.OrderStatusLog.get_or_create(
			order_id=order.order_id,
			from_status=from_status,
			to_status=to_status,
			operator=operator
		)
		return order_status_log