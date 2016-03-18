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

from core.exceptionutil import unicode_full_stack
from wapi.decorators import param_required
#from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model
from db.account import weixin_models as weixin_user_models
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.mall.order_products import OrderProducts
import db.account.models as accout_models

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
		#TODO delete
		#print '>>>>>>>>>>>pay_interface_type:',pay_interface_type,'>>>>>>>>>>>webapp_owner.pay_interfaces>>>>', webapp_owner.pay_interfaces
		try:
			if pay_interface_type != None:
				self.context['interface'] = next(interface for interface in webapp_owner.all_pay_interfaces if interface['type'] == pay_interface_type)
			elif interface_id:
				self.context['interface'] = next(interface for interface in webapp_owner.all_pay_interfaces if interface['id'] == interface_id)

			interface = self.context['interface']
			self.type = interface['type']
			self.related_config_id = interface['related_config_id']
		except:
			interface = None
			self.type = pay_interface_type
			self.related_config_id = None
		

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
				'type': order.pay_interface_type,
				'woid': webapp_owner_id,
				'order_id': order.order_id,
				'pay_interface_type': order.pay_interface_type,
				'is_active': True
			}

		if mall_models.PAY_INTERFACE_ALIPAY == interface_type:
			return {
				'type': 'alipay',
				'woid': webapp_owner_id,
				'order_id': order.order_id,
				'pay_interface_type': mall_models.PAY_INTERFACE_ALIPAY,
				'pay_url':  '/mall/alipay/?woid={}&order_id={}&related_config_id={}'.format(webapp_owner_id, order.order_id, interface['related_config_id']),
				'is_active': interface['is_active']
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
				'pay_interface_type': mall_models.PAY_INTERFACE_COD,
				'is_active': interface['is_active']
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
				'showwxpaytitle': 1,
				'is_active': interface['is_active']
			}
			# return '/wapi/mall/wxpay/?woid={}&order_id={}&pay_id={}&showwxpaytitle=1'.format(
			# 	webapp_owner_id,
			# 	order.order_id,
			# 	interface['id'])
		else:
			return ''


	def get_order_pay_info_for_pay_module(self,order):
		"""
		用于pay模块的订单支付信息
		@param order:
		@return:
		"""
		interface = self.context['interface']
		interface_type = interface['type']
		webapp_owner_id = self.context['webapp_owner'].id

		if interface_type == mall_models.PAY_INTERFACE_WEIXIN_PAY:
			try:
				component_authed_appid = weixin_user_models.ComponentAuthedAppid.select().dj_where(user_id=webapp_owner_id)[0]
				component_info = component_authed_appid.component_info
				component_appid = component_info.app_id

			except:
				component_appid = ''

			return {
				'pay_interface_related_config_id': self.related_config_id,
				'pay_interface_type': interface_type,
				'pay_version': self.pay_config['pay_version'],
				'component_appid': component_appid,
				'app_id': self.pay_config['app_id']
			}
		elif mall_models.PAY_INTERFACE_ALIPAY == interface_type:
			pay_config = self.pay_config
			return {
				'pay_r_id': pay_config['id'],
				'partner': pay_config['partner'],
				'key': pay_config['key'],
				'input_charset': pay_config['input_charset'],
				'sign_type': pay_config['sign_type'],
				'seller_email': pay_config['seller_email']
			}
		else:
			return {}


	def wx_package_for_pay_module(self):
		"""
		用于pay模块的微信package信息
		@return:
		"""
		pay_config = self.pay_config
		pay_version = self.pay_config['pay_version']

		if pay_version == mall_models.V2:
			package_info = {
				'pay_r_id': pay_config['id'],
				'partner_id': pay_config['partner_id'],
				'partner_key': pay_config['partner_key'],
				'paysign_key': pay_config['paysign_key'],
				'app_id': pay_config['app_id'],
				'app_secret': pay_config['app_secret'],
				'pay_version': pay_config['pay_version']
			}
		elif pay_version == mall_models.V3:
			package_info = {
				'pay_r_id': pay_config['id'],
				'app_id': pay_config['app_id'],
				'mch_id': pay_config['partner_id'],
				'partner_key': pay_config['partner_key'],
				'pay_version': pay_config['pay_version']
			}
		else:
			package_info = {}
		return package_info

	@cached_context_property
	def pay_config(self):
		"""
		[property] 与支付接口关联的具体支付配置
		"""
		interface = self.context['interface']
		if interface['type'] == mall_models.PAY_INTERFACE_WEIXIN_PAY:
			weixin_pay_config = mall_models.UserWeixinPayOrderConfig.get(id=interface['related_config_id'])
			return weixin_pay_config.to_dict()
		elif interface['type'] == mall_models.PAY_INTERFACE_ALIPAY:
			ali_pay_config = mall_models.UserAlipayOrderConfig.get(id=interface['related_config_id'])
			return ali_pay_config.to_dict()
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
		elif mall_models.PAY_INTERFACE_PREFERENCE == self.type:
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

	@staticmethod
	def get_order_pay_interfaces(webapp_owner, webapp_user, order_id):
		products = [h.product for h in mall_models.OrderHasProduct.select().dj_where(order_id=order_id)]

		pay_interfaces = [pay_interface for pay_interface in webapp_owner.pay_interfaces if
		                  pay_interface['is_active'] and not pay_interface['type'] == mall_models.PAY_INTERFACE_WEIZOOM_COIN]

		types = [p['type'] for p in pay_interfaces]

		# 如果不包含货到付款，直接返回所有的在线支付
		if mall_models.PAY_INTERFACE_COD not in types:
			return pay_interfaces

		# 商品中是 货到付款方式
		pay_interface_cod_count = 0
		for product in products:
			if product.is_use_cod_pay_interface:
				pay_interface_cod_count = pay_interface_cod_count + 1

		if pay_interface_cod_count == len(list(products)):
			return pay_interfaces
		else:
			# return pay_interfaces.filter(type__in = ONLINE_PAY_INTERFACE)
			return [pay_interface for pay_interface in pay_interfaces if
			        pay_interface['type'] in mall_models.ONLINE_PAY_INTERFACE]
