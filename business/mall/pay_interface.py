# -*- coding: utf-8 -*-
"""@package business.mall.pay_interface
支付接口

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
from core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.mall.order_products import OrderProducts


class PayInterface(business_model.Model):
	"""支付接口
	"""
	__slots__ = (
		'type',
		'related_config_id'
	)

	@staticmethod
	@param_required(['webapp_owner', 'interface_id'])
	def from_id(args):
		"""工厂方法，根据支付接口的id创建PayInterface对象

		@param [in] interface_id : 支付接口的id

		@return PayInterface业务对象
		"""
		pay_interface = PayInterface(args['webapp_owner'], interface_id=int(args['interface_id']))
		return pay_interface

	@staticmethod
	@param_required(['webapp_owner', 'pay_interface_type'])
	def from_type(args):
		"""工厂方法，根据支付接口类型创建PayInterface对象

		@param [in] pay_interface_type : 支付接口的类型

		@return PayInterface业务对象
		"""
		pay_interface = PayInterface(args['webapp_owner'], pay_interface_type=int(args['pay_interface_type']))
		return pay_interface

	def __init__(self, webapp_owner, pay_interface_type=None, interface_id=None):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner

		if pay_interface_type != None:
			self.context['interface'] = next(interface for interface in webapp_owner.pay_interfaces if interface['type'] == pay_interface_type)
		elif interface_id:
			self.context['interface'] = next(interface for interface in webapp_owner.pay_interfaces if interface['id'] == interface_id)

		interface = self.context['interface']
		self.type = interface['type']
		self.related_config_id = interface['related_config_id']

	def get_pay_url_info_for_order(self, order):
		"""获取订单的支付链接

		@param[in] order: 代支付的订单

		@return 支付链接
		"""
		interface = self.context['interface']
		interface_type = interface['type']
		webapp_owner_id = self.context['webapp_owner'].id

		if order.final_price == 0:
			return {
				'type': 'cod',
				'woid': webapp_owner_id,
				'order_id': order.order_id,
				'pay_interface_type': mall_models.PAY_INTERFACE_COD
			}
			
		if mall_models.PAY_INTERFACE_ALIPAY == interface_type:
			return {
				'type': 'alipay',
				'woid': webapp_owner_id,
				'order_id': order.order_id,
				'pay_interface_type': mall_models.PAY_INTERFACE_ALIPAY,
				'pay_url':  '/mall/alipay/?woid={}&order_id={}&related_config_id={}'.format(webapp_owner_id, order.order_id, interface['related_config_id'])
			}

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
			return {
				'type': 'cod',
				'woid': webapp_owner_id,
				'order_id': order.order_id,
				'pay_interface_type': mall_models.PAY_INTERFACE_COD
			}
			# return '/wapi/mall/pay_result/?woid={}&pay_interface_type={}&order_id={}'.format(
			# 	webapp_owner_id,
			# 	mall_models.PAY_INTERFACE_COD,
			# 	order.order_id)
		elif mall_models.PAY_INTERFACE_WEIXIN_PAY == interface_type:
			return {
				'type': 'wxpay',
				'woid': webapp_owner_id,
				'order_id': order.order_id,
				'pay_id': interface['id'],
				'showwxpaytitle': 1
			}
			# return '/wapi/mall/wxpay/?woid={}&order_id={}&pay_id={}&showwxpaytitle=1'.format(
			# 	webapp_owner_id,
			# 	order.order_id,
			# 	interface['id'])
		else:
			return ''

	@cached_context_property
	def pay_config(self):
		"""
		[property] 与支付接口关联的具体支付配置
		"""
		interface = self.context['interface']
		if interface['type'] == mall_models.PAY_INTERFACE_WEIXIN_PAY:
			weixin_pay_config = mall_models.UserWeixinPayOrderConfig.get(id=interface['related_config_id'])
			return weixin_pay_config.to_dict()
		else:
			return None

	def parse_pay_result(self, pay_result):
		"""解析支付结果

		@param[in] pay_result: 第三方支付接口返回的支付结果信息

		@return 支付结果
			is_success: 支付是否成功
			order_id: 支付的订单的id
			error_msg: 如果is_success为False, error_msg中给出失败的原因
		"""
		error_msg = ''
		if mall_models.PAY_INTERFACE_ALIPAY == self.type:
			order_id = pay_result.get('out_trade_no', None)
			trade_status = pay_result.get('result', '')
			is_trade_success = ('success' == trade_status.lower())
		elif mall_models.PAY_INTERFACE_TENPAY == self.type:
			trade_status = int(pay_result.get('trade_status', -1))
			is_trade_success = (0 == trade_status)
			error_msg = pay_result.get('pay_info', '')
			order_id = pay_result.get('out_trade_no', None)
		elif mall_models.PAY_INTERFACE_COD == self.type:
			is_trade_success = True
			order_id = pay_result.get('order_id')
		elif mall_models.PAY_INTERFACE_WEIXIN_PAY == self.type:
			is_trade_success = True
			order_id = pay_result.get('order_id')
		else:
			pass

		#兼容改价
		try:
			order_id = order_id.split('-')[0]
		except:
			pass

		return {
			'is_success': is_trade_success,
			'order_id': order_id,
			'error_msg': error_msg
		}



