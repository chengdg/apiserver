# -*- coding: utf-8 -*-

import copy
from datetime import datetime

from eaglet.core import api_resource
from eaglet.decorator import param_required
from db.mall import models as mall_models
from db.mall import promotion_models
from util import dateutil as utils_dateutil
#import resource
from business.mall.purchase_info import PurchaseInfo
from business.mall.purchase_order import PurchaseOrder
from business.mall.forbidden_coupon_product_ids import ForbiddenCouponProductIds
from business.mall.supplier_postage_config import SupplierPostageConfig

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

		# today = datetime.today()
		# product_ids = set()
		# total_price = 0
		# productIds2original_price = dict()
		# is_all_product_forbidden_coupon = True
		# for product in products:
		# 	product_ids.add(product.id)
		# 	product_total_price = product.price * product.purchase_count
		# 	product_total_original_price = product.original_price * product.purchase_count
		# 	if not product.id in forbidden_coupon_product_ids:
		# 		#没有禁用优惠券的商品的金额才累计进入总价
		# 		total_price += product_total_price
		# 		is_all_product_forbidden_coupon = False

		# 	if not productIds2original_price.get(product.id):
		# 		productIds2original_price[product.id] = 0
		# 	productIds2original_price[product.id] += product_total_original_price

		# for coupon in coupons:
		# 	can_use_coupon = True
		# 	if not coupon.is_can_use_by_webapp_user(webapp_user):
		# 		can_use_coupon = False
		# 	else:
		# 		if coupon.is_specific_product_coupon():
		# 			#单品券
		# 			if (not coupon.limit_product_id in product_ids) or (coupon.valid_restrictions > productIds2original_price[coupon.limit_product_id]):
		# 				coupon.disable()
		# 				can_use_coupon = False
		# 		else:
		# 			#通用券
		# 			if is_all_product_forbidden_coupon:
		# 				#所有的商品都禁用了优惠券，通用券必须禁用
		# 				coupon.disable()
		# 				can_use_coupon = False
		# 			if coupon.valid_restrictions > total_price:
		# 				coupon.disable()
		# 				can_use_coupon = False

		# 	if can_use_coupon:
		# 		result_coupons.append(coupon.to_dict())
		# 	else:
		# 		limit_coupons.append(coupon.to_dict())

		for coupon in coupons:
			can_use_coupon, _ = coupon.is_can_use_for_products(webapp_user, products)

			if can_use_coupon:
				result_coupons.append(coupon.to_dict())
			else:
				limit_coupons.append(coupon.to_dict())

		return result_coupons, limit_coupons

	@param_required([])
	def get(args):
		"""
		获取购物车项目

		@param 无
		@return
		{
			'order': order_info,
			'enable_wzcard': webapp_owner.has_wzcard_permission,
			'mall_config': mall_config,
			'integral_info': integral_info,
			'coupons': coupons,
			'limit_coupons': limit_coupons,
			'use_ceiling': use_ceiling,
			'postage_factor': postage_factor
		}
		"""

		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		member = args.get('member', None)

		group_id = args.get('group_id', '')

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

		#获取商城配置
		mall_config = webapp_owner.mall_config
		use_ceiling = webapp_owner.integral_strategy_settings.use_ceiling

		#product_supplier_ids = [product.supplier for product in order.products]
		#product_supplier_configs = None #供货商运费配置信息
		#自营平台和商家分开处理
		if webapp_owner.user_profile.webapp_type:
			supplier_product_groups = []
			for key, value in sorted(order.promotion_product_groups.iteritems(), key=lambda d:d[0]):
				supplier_product_groups.append([group.to_dict(with_price_factor=True, with_coupon_info=True) for group in order.promotion_product_groups[key]])
			product_group_datas = supplier_product_groups
			#product_supplier_configs = SupplierPostageConfig.get_supplier_postage_config_by_supplier({'supplier_ids': product_supplier_ids})
			#product_group_datas = SupplierPostageConfig.product_group_use_supplier_postage({'product_groups': product_group_datas, 'supplier_ids': product_supplier_ids})
		else:
			product_group_datas = [group.to_dict(with_price_factor=True, with_coupon_info=True) for group in order.promotion_product_groups]
		order_info = {
			'type': order.type,
			'pay_interfaces': order.pay_interfaces,
			'product_groups': product_group_datas,
			'is_enable_bill': order.is_enable_bill,
			'is_delivery': order.is_delivery # 是否勾选配送时间,发货时间判断字段
		}
		usable_cards = [card.to_dict() for card in webapp_user.wzcard_package.usable_cards]

		return {
			'order': order_info,
			'enable_wzcard': webapp_owner.has_wzcard_permission,
			'mall_config': mall_config,
			'integral_info': integral_info,
			'coupons': coupons,
			'limit_coupons': limit_coupons,
			'use_ceiling': use_ceiling,
			'postage_factor': postage_factor,
			'group_id': group_id,
			'usable_cards': usable_cards,
			'mall_type': webapp_owner.user_profile.webapp_type,
			#'product_supplier_configs': product_supplier_configs
		}

