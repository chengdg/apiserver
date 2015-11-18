# -*- coding: utf-8 -*-

"""支付接口

"""

import json
from bs4 import BeautifulSoup
import math
import itertools
import uuid
import time
import random

from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.mall.order_products import OrderProducts
from business.mall.product_grouper import ProductGrouper
from business.mall.order_checker import OrderChecker


class PayInterface(business_model.Model):
	"""支付接口
	"""
	__slots__ = (
		'id',
		'order_id',
		'pay_interface_type',
		'final_price',
	)

	@staticmethod
	@param_required(['webapp_owner', 'pay_interface_type'])
	def from_type(args):
		"""工厂方法，创建PayInterface对象

		@param [in] pay_interface_type : 支付接口的类型

		@return Order对象
		"""
		pay_interface = PayInterface(args['webapp_owner'], int(args['pay_interface_type']))
		return pay_interface

	def __init__(self, webapp_owner, pay_interface_type):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner

		self.context['interface'] = next(interface for interface in webapp_owner.pay_interfaces if interface['type'] == pay_interface_type)

	def get_pay_url_for_order(self, order):
		interface = self.context['interface']
		interface_type = interface['type']
		webapp_owner_id = self.context['webapp_owner'].id
		if mall_models.PAY_INTERFACE_ALIPAY == interface_type:
			return '/mall/alipay/?woid={}&order_id={}&related_config_id={}'.format(webapp_owner_id, order.order_id, interface['related_config_id'])
		elif mall_models.PAY_INTERFACE_TENPAY == interface_type:
			# from account.models import UserProfile
			# user_profile = UserProfile.objects.get(user_id=webapp_owner_id)
			# call_back_url = "http://{}/tenpay/mall/pay_result/get/{}/{}/".format(
			# 	user_profile.host,
			# 	webapp_owner_id,
			# 	self.related_config_id)
			# notify_url = "http://{}/tenpay/mall/pay_notify_result/get/{}/{}/".format(
			# 	user_profile.host,
			# 	webapp_owner_id,
			# 	self.related_config_id)
			# pay_submit = TenpaySubmit(
			# 	self.related_config_id,
			# 	order,
			# 	call_back_url,
			# 	notify_url)
			# tenpay_url = pay_submit.submit()

			# return tenpay_url
			#不再支持财付通
			return ''
		elif mall_models.PAY_INTERFACE_COD == interface_type:
			return '/mall/pay_result/?woid={}&pay_interface_type={}&order_id={}'.format(
				webapp_owner_id,
				PAY_INTERFACE_COD,
				order.order_id)
		elif mall_models.PAY_INTERFACE_WEIXIN_PAY == interface_type:
			return '/mall/wxpay/?woid={}&order_id={}&pay_id={}&showwxpaytitle=1'.format(
				webapp_owner_id,
				order.order_id,
				interface['id'])
		else:
			return ''
