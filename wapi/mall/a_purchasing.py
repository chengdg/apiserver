# -*- coding: utf-8 -*-

import copy
from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from utils import dateutil as utils_dateutil
import resource
from business.mall.purchase_info import PurchaseInfo
from business.mall.purchase_order import PurchaseOrder


class APurchasing(api_resource.ApiResource):
	"""
	下单页数据
	"""
	app = 'mall'
	resource = 'purchasing'

	def __get_coupons(webapp_user, products):
		coupons = webapp_user.all_coupons 
		limit_coupons = []
		result_coupons = []
		if len(coupons) == 0:
			return result_coupons, limit_coupons

		today = datetime.today()
		product_ids = set()
		total_price = 0
		productIds2original_price = dict()
		is_forbidden_coupon = True
		for product in products:
			product_ids.add(product.id)
			product_total_price = product.price * product.purchase_count
			product_total_original_price = product.original_price * product.purchase_count
			total_price += product_total_price

			if not productIds2original_price.get(product.id):
				productIds2original_price[product.id] = 0
			productIds2original_price[product.id] += product_total_original_price

		for coupon in coupons:
			can_use_coupon = True
			if not coupon.is_can_use_by_webapp_user(webapp_user):
				can_use_coupon = False
			else:
				if coupon.is_specific_product_coupon():
					#单品券
					if (not coupon.limit_product_id in product_ids) or (coupon.valid_restrictions > productIds2original_price[coupon.limit_product_id]):
						coupon.disable()
						can_use_coupon = False
				else:
					#通用券
					if coupon.valid_restrictions > total_price:
						coupon.disable()
						can_use_coupon = False

			if can_use_coupon:
				result_coupons.append(coupon.to_dict())
			else:
				limit_coupons.append(coupon.to_dict())

		return result_coupons, limit_coupons

	@param_required([])
	def get(args):
		"""
		获取购物车项目

		@param id 商品ID
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		member = args.get('member', None)

		purchase_info = PurchaseInfo.parse({
			'request_args': args
		})

		order = PurchaseOrder.create({
			"webapp_owner": webapp_owner,
			"webapp_user": webapp_user,
			"purchase_info": purchase_info,
		})

		#获得运费配置，支持前端修改数量、优惠券等后实时计算运费
		postage_factor = webapp_owner.system_postage_config['factor']

		#获取积分信息
		integral_info = webapp_user.integral_info
		integral_info['have_integral'] = (integral_info['count'] > 0)

		#获取优惠券
		coupons, limit_coupons = APurchasing.__get_coupons(webapp_user, order.products)
		print '-*-' * 20
		print coupons
		print limit_coupons
		print '-*-' * 20
		#coupons, limit_coupons = [], []

		#获取商城配置
		mall_config = webapp_owner.mall_config
		use_ceiling = webapp_owner.integral_strategy_settings.use_ceiling

		product_group_datas = [group.to_dict(with_price_factor=True) for group in order.promotion_product_groups]

		order_info = {
			'type': order.type,
			'ship_name': order.ship_info['name'],
			'ship_tel': order.ship_info['tel'],
			'ship_address': order.ship_info['address'],
			'ship_id': order.ship_info['id'],
			'ship_area': order.ship_info['area'],
			'display_ship_area': order.ship_info['display_area'],
			'pay_interfaces': order.pay_interfaces,
			'product_groups': product_group_datas
		}

		return {
			'order': order_info,
			'mall_config': mall_config,
			'integral_info': integral_info,
			'coupons': coupons,
			'limit_coupons': limit_coupons,
			'use_ceiling': use_ceiling,
			'postage_factor': postage_factor
		}

