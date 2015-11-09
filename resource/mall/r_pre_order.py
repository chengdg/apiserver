# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup
import math

#from core import resource
from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
import settings
import resource
from core import inner_resource
from core.watchdog.utils import watchdog_alert


class RPreOrder(inner_resource.Resource):
	"""
	商品详情
	"""
	app = 'mall'
	resource = 'pre_order'

	@staticmethod
	def has_can_use_by_coupon_id(coupon_id, owner_id, product_prices, product_ids, member_id, products=None, original_prices=None, product_id2price=None):
		"""
		优惠券是否可用
		"""
		if coupon_id is None or coupon_id < 0:
			return '请输入正确的优惠券号', None

		coupon = promotion_models.Coupon.objects.filter(coupon_id=coupon_id,owner_id=owner_id)
		if len(coupon) > 0:
			coupon = coupon[0]
			today = datetime.today()
			if coupon.expired_time < today or coupon.status == promotion_models.COUPON_STATUS_EXPIRED:
				return '该优惠券已过期', None
			elif coupon.status == promotion_models.COUPON_STATUS_Expired:
				return '该优惠券已失效', None
			elif coupon.status == promotion_models.COUPON_STATUS_DISCARD:
				return '该优惠券已作废', None
			elif coupon.status == promotion_models.COUPON_STATUS_USED:
				return '该优惠券已使用', None
			if coupon.member_id > 0 and coupon.member_id != member_id:
				return '该优惠券已被他人领取不能使用', None
			coupon_rule = promotion_models.CouponRule.objects.get(id=coupon.coupon_rule_id)
			if coupon_rule.start_date > today:
				return'该优惠券活动尚未开始', None

			order_price = sum(product_prices)
			if coupon_rule.limit_product:
				promotion = promotion_models.Promotion.objects.get(detail_id=coupon_rule.id, type=promotion_models.PROMOTION_TYPE_COUPON)
				cant_use_coupon = True
				for relation in promotion_models.ProductHasPromotion.objects.filter(promotion_id=promotion.id):
					if str(relation.product_id) in product_ids:
						# 单品券商品在订单列表中
						price = 0
						for i in range(len(product_ids)):
							if product_ids[i] == str(relation.product_id):
								if products:
									for p in products:
										if p.id == relation.product_id:
											price += p.original_price * p.purchase_count
											order_price = order_price + (p.original_price - p.price) * p.purchase_count
								else:
									price += original_prices[i]
									order_price = order_price + original_prices[i] - product_prices[i]
						if coupon_rule.valid_restrictions > 0:
							# 单品券限制购物金额

							if coupon_rule.valid_restrictions > price:
								return '该优惠券指定商品金额不满足使用条件', None
						# 单品券只抵扣单品金额
						if price < coupon.money:
							coupon.money = round(price, 2)
						cant_use_coupon = False
				if cant_use_coupon:
					return '该优惠券不能购买订单中的商品', None
			else:
				#通用优惠券判断逻辑 duhao 20150909
				from cache import webapp_cache
				is_forbidden = True
				forbidden_coupon_product_ids = webapp_cache.get_forbidden_coupon_product_ids(owner_id)
				for product_id in product_ids:
					product_id = int(product_id)
					if not product_id in forbidden_coupon_product_ids:
						is_forbidden = False

				if is_forbidden:
					return '该优惠券不能购买订单中的商品', None

				if product_id2price and len(product_id2price) > 0:
					order_price = 0.0
					for product_id in product_id2price:
						#被禁用全场优惠券的商品在计算满额可用券时要排除出去，不参与计算 duhao
						if not int(product_id) in forbidden_coupon_product_ids:
							order_price += product_id2price[product_id]

			coupon.money = float(coupon.money)
			if coupon_rule.valid_restrictions > order_price and coupon_rule.valid_restrictions != -1:
				return '该优惠券不满足使用金额限制', None
			return '', coupon
		else:
			return '请输入正确的优惠券号', None

	@staticmethod
	def check_products(webapp_owner_id, pre_order, request_args):
		"""
		检查是否有商品下架
		"""
		products = pre_order.products
		off_shelve_products = [product for product in products if product.shelve_type == PRODUCT_SHELVE_TYPE_OFF]
		if len(off_shelve_products) > 0:
			if len(off_shelve_products) == len(products):
				#所有商品下架，返回商品列表页
				return {
					'success': False,
					'data': {
						'msg': u'商品已下架<br/>2秒后返回商城首页',
						'redirect_url': '/workbench/jqm/preview/?module=mall&model=products&action=list&category_id=0&workspace_id=mall&woid=%s' % request.user_profile.user_id
					}
				}
			else:
				return {
					'success': False,
					'data': {
						'msg': u'有商品已下架<br/>2秒后返回购物车<br/>请重新下单',
						'redirect_url': '/workbench/jqm/preview/?module=mall&model=shopping_cart&action=show&workspace_id=mall&woid=%s' % request.user_profile.user_id
					}
				}
		else:
			return {
				'success': True
			}

	@staticmethod
	def check_coupon(webapp_owner_id, pre_order, request_args):
		"""
		检查优惠券
		"""
		if not hasattr(pre_order, 'session_data'):
			pre_order.session_data = dict()
		fail_msg = {
			'success': False,
			'data': {
				'msg': u'',
				'redirect_url': 'http://h5.weapp.com/mall/shopping_cart/?woid=%s' % webapp_owner_id
			}
		}
		is_use_coupon = (request_args.get('is_use_coupon', 'false') == 'true')
		if is_use_coupon:
			coupon_id = request_args.get('coupon_id', 0)
			#modified by duhao 20150909
			# product_prices = [product.price * product.purchase_count for product in pre_order.products]
			# product_ids = [str(product.id) for product in pre_order.products]
			product_prices = []
			product_ids = []
			product_id2price = {}
			for product in pre_order.products:
				price = product.price * product.purchase_count
				product_ids.append(str(product.id))
				product_prices.append(price)
				if not product_id2price.has_key(product.id):
					#用于处理同一商品买了不同规格的情况
					product_id2price[product.id] = 0.0

				product_id2price[product.id] += price

			from market_tools.tools.coupon import util as coupon_util
			msg, coupon = coupon_util.has_can_use_by_coupon_id(coupon_id, request.webapp_owner_id, product_prices, product_ids, request.member.id, products=pre_order.products, product_id2price=product_id2price)
			if coupon:
				pre_order.session_data['coupon'] = coupon
			else:
				fail_msg['data']['msg'] = msg
				return fail_msg
		return {
			'success': True
		}

	@param_required(['woid', 'webapp_user', 'member', 'products', 'request_args'])
	def get(args):
		webapp_owner_id = args['woid']
		webapp_user = args['webapp_user']
		webapp_owner_info = args['webapp_owner_info']
		member = args['member']
		products = args['products']
		request_args = args['request_args']

		order = cache_util.Object("pre_order")
		order.products = products

		#按促销进行product分组
		order.product_groups = resource.get('mall', 'product_groups', {
			'webapp_owner_info': webapp_owner_info,
			'member': member,
			'products': products
		})

		#检查order的有效性
		for checker in RPreOrder.checkers:
			result = checker(webapp_owner_id, products, request_args)

RPreOrder.checkers = [
	RPreOrder.check_products
]