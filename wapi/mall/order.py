# -*- coding: utf-8 -*-

import copy
from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from wapi.mall import models as mall_models
from wapi.mall import promotion_models
from utils import dateutil as utils_dateutil
import resource
from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
from cache import utils as cache_utils
from business.mall.b_pre_order import BPreOrder


class Order(api_resource.ApiResource):
	"""
	订单
	"""
	app = 'mall'
	resource = 'order'

	@param_required(['woid', 'webapp_user', 'ship_name', 'ship_address', 'ship_tel', 'order_type', 'xa-choseInterfaces'])
	def put(args):
		"""
		获取购物车项目

		@param id 商品ID
		"""
		webapp_user = args['webapp_user']
		webapp_owner_id = args['woid']
		member = args.get('member', None)
		webapp_owner_info = webapp_user.webapp_owner_info
		profile = args['webapp_owner_profile']
		webapp_id = profile.webapp_id
		ship_name = args['ship_name']
		ship_address = args['ship_address']
		ship_tel = args['ship_tel']
		order_type = args.get('order_type', mall_models.PRODUCT_DEFAULT_TYPE)
		pay_interface = args.get('xa-choseInterfaces', '-1')
		refueling_order = args.get('refueling_order', '')
		area = args.get('area', '') #地址信息
		bill_type = mall_models.ORDER_BILL_TYPE_NONE #发票
		customer_message = args.get('message', '') #用户留言

		product_info = PurchasingApiResource.get_product_param(args)
		products = resource.get('mall', 'order_products', {
			"woid": webapp_owner_id,
			"webapp_owner_info": webapp_owner_info,
			"webapp_user": webapp_user,
			"member": member,
			"product_info": product_info
		})

		pre_order = BPreOrder.get({
			'woid': webapp_owner_id,
			'webapp_owner_info': webapp_owner_info,
			'webapp_user': webapp_user,
			'member': member,
			'products': products,
			'request_args': args
		})

		pre_order_validation = pre_order.check_validation()

		if (not pre_order_validation['is_valid']):
			return 500, pre_order_validation['reason']
		#如果pre_order不有效，直接返回

		# 发送下单检查信号

		#创建order对象
		order = resource.get('mall', 'order', {
			'woid': webapp_owner_id,
			'webapp_owner_info': webapp_owner_info,
			'webapp_user': webapp_user,
			'member': member,
			'products': products
		})

		#获得运费配置，支持前端修改数量、优惠券等后实时计算运费
		postage_factor = product.postage_config['factor']

		#获取积分信息
		integral_info = webapp_user.integral_info
		integral_info['have_integral'] = (integral_info['count'] > 0)

		#获取优惠券
		coupons, limit_coupons = Purchasing.__fill_coupons_for_edit_order(webapp_owner_id, webapp_user, products)

		#获取商城配置
		mall_config = webapp_owner_info.mall_data['mall_config']#MallConfig.objects.get(owner_id=webapp_owner_id)
		use_ceiling = webapp_owner_info.integral_strategy_settings.use_ceiling

		return {
			'order': order,
			'mall_config': mall_config,
			'integral_info': integral_info,
			'coupons': coupons,
			'limit_coupons': limit_coupons,
			'use_ceiling': use_ceiling,
			'postage_factor': postage_factor,
			'product_groups': Purchasing.__format_product_group_price_factor(order['product_groups'], webapp_owner_id)
		}