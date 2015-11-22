# -*- coding: utf-8 -*-

import json

from bs4 import BeautifulSoup

from core import inner_resource
from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from wapi.mall import models as mall_models
import settings
from core.watchdog.utils import watchdog_alert


class RProductPayInterfaces(inner_resource.Resource):
	"""
	商品详情
	"""
	app = 'mall'
	resource = 'product_pay_interfaces'


	@param_required(['webapp_user', 'products'])
	def get(args):
		"""
		module_api.__get_products_pay_interfaces
		"""
		webapp_user = args['webapp_user']
		products = args['products']
		
		pay_interfaces = [pay_interface for pay_interface in webapp_user.webapp_owner_info.pay_interfaces if pay_interface.is_active and not pay_interface.type == mall_models.PAY_INTERFACE_WEIZOOM_COIN]

		types = [p.type for p in pay_interfaces]

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
			return [pay_interface for pay_interface in pay_interfaces if pay_interface.type in mall_models.ONLINE_PAY_INTERFACE]

