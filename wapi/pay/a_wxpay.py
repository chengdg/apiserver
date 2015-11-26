# -*- coding: utf-8 -*-

import copy
from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from utils import dateutil as utils_dateutil
import resource
from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
from core.cache import utils as cache_utils
from business.mall.order import Order
from business.mall.pay_interface import PayInterface
import settings


class AWXPay(api_resource.ApiResource):
	"""
	订单
	"""
	app = 'pay'
	resource = 'wxpay'

	@param_required(['order_id', 'pay_id'])
	def get(args):
		"""
		获取购物车项目

		@param id 商品ID
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		order_id = args['order_id']
		interface_id = args['pay_id']
		is_oauthed = ('code' in args)
		
		pay_interface = PayInterface.from_id({
			'webapp_owner': webapp_owner,
			'interface_id': interface_id
		})
		weixin_pay_config = pay_interface.pay_config

		order = Order.from_id({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user,
			'order_id': order_id
		})

		data = {}
		data['app_id'] = weixin_pay_config['app_id']
		data['partner_id'] = weixin_pay_config['partner_id']
		data['partner_key'] = weixin_pay_config['partner_key']
		data['paysign_key'] = weixin_pay_config['paysign_key']
		data['app_secret'] = weixin_pay_config['app_secret']
		data['pay_version'] = weixin_pay_config['pay_version']
		data['total_fee_display'] = order.final_price
		data['total_fee'] = int(order.final_price * 100)	

		if data['pay_version'] == 0 or (bool(is_oauthed) and data['pay_version'] != 0):
			product_outlines = order.product_outlines

			product_names = ','.join([product_outline.name for product_outline in product_outlines])
			if len(product_names) > 127:
				product_names = product_names[:127]
			
			if order.edit_money:
				data['order_id'] = '{}-{}'.format(order_id, str(order.edit_money).replace('.','').replace('-',''))
			else:
				data['order_id'] = order_id
			data['domain'] = settings.PAY_HOST
			data['webapp_owner_id'] = webapp_owner.id
			data['pay_interface_type'] = pay_interface.type
			data['pay_interface_related_config_id'] = pay_interface.related_config_id
			data['product_names'] = product_names
			data['user_ip'] = '181.181.181.181'

		return data

	@param_required(['woid', 'ship_name', 'ship_address', 'ship_tel', 'order_type', 'xa-choseInterfaces'])
	def put(args):
		"""
		获取购物车项目

		@param id 商品ID
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		
		return {}


