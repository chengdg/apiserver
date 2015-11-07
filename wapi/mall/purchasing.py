# -*- coding: utf-8 -*-

import copy

from core import api_resource
from wapi.decorators import param_required
from wapi.mall import models as mall_models
from utils import dateutil as utils_dateutil
import resource


class Purchasing(api_resource.ApiResource):
	"""
	购物车项目
	"""
	app = 'mall'
	resource = 'purchasing'

	def get_product_param(args):
	    '''获取订单商品id，数量，规格
	    供_get_products调用
	    '''
	    if 'redirect_url_query_string' in args:
	        query_string = Purchasing.get_query_string_dict_to_str(args['redirect_url_query_string'])
	    else:
	        query_string = args

	    if 'product_ids' in query_string:
	        product_ids = query_string.get('product_ids', None)
	        if product_ids:
	            product_ids = product_ids.split('_')
	        promotion_ids = query_string.get('promotion_ids', None)
	        if promotion_ids:
	            promotion_ids = promotion_ids.split('_')
	        else:
	            promotion_ids = [0] * len(product_ids)
	        product_counts = query_string.get('product_counts', None)
	        if product_counts:
	            product_counts = product_counts.split('_')
	        product_model_names = query_string.get('product_model_names', None)
	        if product_model_names:
	            if '$' in product_model_names:
	                product_model_names = product_model_names.split('$')
	            else:
	                product_model_names = product_model_names.split('%24')
	        product_promotion_ids = query_string.get('product_promotion_ids', None)
	        if product_promotion_ids:
	            product_promotion_ids = product_promotion_ids.split('_')
	        product_integral_counts = query_string.get('product_integral_counts', None)
	        if product_integral_counts:
	            product_integral_counts = product_integral_counts.split('_')
	    else:
	        product_ids = [query_string.get('product_id', None)]
	        promotion_ids = [query_string.get('promotion_id', None)]
	        product_counts = [query_string.get('product_count', None)]
	        product_model_names = [query_string.get('product_model_name', 'standard')]
	        product_promotion_ids = [query_string.get('product_promotion_id', None)]
	        product_integral_counts = [query_string.get('product_integral_count', None)]

	    return {
	    	"product_ids": product_ids,
	    	"promotion_ids": promotion_ids,
	    	"product_counts": product_counts,
	    	"product_model_names": product_model_names
	    }

	@staticmethod
	def get_query_string_dict_to_str(str):
	    data = dict()
	    for item in str.split('&'):
	        values = item.split('=')
	        data[values[0]] = values[1]
	    return data

	def __fill_coupons_for_edit_order(webapp_owner_id, webapp_user, products):
		"""
		request_util:__fill_coupons_for_edit_order
		"""
		coupons = webapp_user.coupons 
		limit_coupons = []
		result_coupons = []
		if len(coupons) == 0:
			return result_coupons, limit_coupons

		today = datetime.today()
		product_ids = []
		total_price = 0
		# jz 2015-10-09
		# productIds2price = dict()
		productIds2original_price = dict()
		is_forbidden_coupon = True
		for product in products:
			product_ids.append(product.id)
			product_total_price = product.price * product.purchase_count
			product_total_original_price = product.original_price * product.purchase_count
			# TODO: 去掉ProductHint的直接调用
			if not ProductHint.is_forbidden_coupon(webapp_owner_id, product.id):
				#不是被禁用全场优惠券的商品 duhao 20150908
				total_price += product_total_price
				is_forbidden_coupon = False
			# jz 2015-10-09
			# if not productIds2price.get(product.id):
			# 	productIds2price[product.id] = 0
			# productIds2price[product.id] += product_total_price

			if not productIds2original_price.get(product.id):
				productIds2original_price[product.id] = 0
			productIds2original_price[product.id] += product_total_original_price
		for coupon in coupons:
			valid = coupon.valid_restrictions
			limit_id = coupon.limit_product_id

			if coupon.start_date > today:
				#兼容历史数据
				if coupon.status == promotion_models.COUPON_STATUS_USED:
					coupon.display_status = 'used'
				else:
					coupon.display_status = 'disable'
				limit_coupons.append(coupon)
			elif coupon.status != promotion_models.COUPON_STATUS_UNUSED:
				# 状态不是未使用
				if coupon.status == promotion_models.COUPON_STATUS_USED:
					# 状态是已使用
					coupon.display_status = 'used'
				else:
					# 过期状态
					coupon.display_status = 'overdue'
				limit_coupons.append(coupon)
			# jz 2015-10-09
			# elif coupon.limit_product_id > 0 and \
			# 	(product_ids.count(limit_id) == 0 or valid > productIds2price[limit_id]) or\
			# 	valid > total_price or\
			# 	coupon.provided_time >= today or is_forbidden_coupon:
			# 	# 1.订单没有限定商品
			# 	# 2.订单金额不足阈值
			# 	# 3.优惠券活动尚未开启
			# 	# 4.订单里面都是被禁用全场优惠券的商品 duhao
			# 	coupon.display_status = 'disable'
			# 	limit_coupons.append(coupon)

			elif coupon.limit_product_id == 0 and (valid > total_price or coupon.provided_time >= today or is_forbidden_coupon):
				#通用券
				# 1.订单金额不足阈值
				# 2.优惠券活动尚未开启
				# 3.订单里面都是被禁用全场优惠券的商品 duhao
				coupon.display_status = 'disable'
				limit_coupons.append(coupon)

			elif coupon.limit_product_id > 0 and (product_ids.count(limit_id) == 0 or valid > productIds2original_price[limit_id]or coupon.provided_time >= today):
				# 单品卷
				# 1.订单金额不足阈值
				# 2.优惠券活动尚未开启
				coupon.display_status = 'disable'
				limit_coupons.append(coupon)
			else:
				result_coupons.append(coupon)

		return result_coupons, limit_coupons

	def __format_product_group_price_factor(product_groups, webapp_owner_id):
		"""
		request_util:__format_product_group_price_factor
		"""
		forbidden_coupon_product_ids = resource.get('mall', 'forbidden_coupon_product_ids', {
			'woid': webapp_owner_id
		})

		factors = []
		for product_group in product_groups:
			product_factors = []
			for product in product_group['products']:
				is_forbidden_coupon = False
				if product['id'] in forbidden_coupon_product_ids:
					is_forbidden_coupon = True
				product_factors.append({
					"id": product['id'],
					"model": product['model_name'],
					"count": product['purchase_count'],
					"price": product['price'],
					"original_price": product['original_price'],
					"weight": product['weight'],
					"active_integral_sale_rule": product.get('active_integral_sale_rule', None),
					"postageConfig": product.get('postage_config', {}),
					"forbidden_coupon": is_forbidden_coupon
				})

			factor = {
				'id': product_group['id'],
				'uid': product_group['uid'],
				'products': product_factors,
				'promotion': product_group['promotion'],
				'promotion_type': product_group['promotion_type'],
				'promotion_result': product_group['promotion_result'],
				'integral_sale_rule': product_group['integral_sale_rule'],
				'can_use_promotion': product_group['can_use_promotion']
			}
			factors.append(factor)

		return factors

	@param_required(['woid', 'webapp_user', 'product_id', 'product_count', 'product_model_name'])
	def get(args):
		"""
		获取购物车项目

		@param id 商品ID
		"""
		webapp_user = args['webapp_user']
		webapp_owner_id = args['woid']
		member = args.get('member', None)
		webapp_owner_info = webapp_user.webapp_owner_info

		product_info = Purchasing.get_product_param(args)
		products = resource.get('mall', 'order_products', {
			"woid": webapp_owner_id,
			"webapp_owner_info": webapp_owner_info,
			"webapp_user": webapp_user,
			"member": member,
			"product_info": product_info
		})
		product = products[0]

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