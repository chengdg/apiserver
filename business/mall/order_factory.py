# -*- coding: utf-8 -*-
"""@package business.mall.order_factory
订单生成器

订单生成器根据购买信息(PurchaseInfo对象)，生成一个订单

通常下单的流程为:
```python
order_factory = OrderFactory.create({
	'webapp_owner': webapp_owner,
	'webapp_user': webapp_user,
	'purchase_info': purchase_info
})

validate_result = order_factory.validate()
if validate_result['is_valid']:
	order = order_factory.save()
```

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
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.mall.order_products import OrderProducts
from business.mall.product_grouper import ProductGrouper
from business.mall.order_checker import OrderChecker
from business.mall.order import Order


class OrderFactory(business_model.Model):
	"""订单生成器
	"""
	__slots__ = (
		'purchase_info',
		'products',
		'product_groups',
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'purchase_info'])
	def create(args):
		"""工厂方法，创建Order对象

		@return Order对象
		"""
		order_factory = OrderFactory(args['webapp_owner'], args['webapp_user'], args['purchase_info'])

		return order_factory

	def __init__(self, webapp_owner, webapp_user, purchase_info):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		#获取订单商品集合
		order_products = OrderProducts.get({
			"webapp_owner": webapp_owner,
			"webapp_user": webapp_user,
			"purchase_info": purchase_info
		})
		self.products = order_products.products

		#按促销进行product分组
		product_grouper = ProductGrouper()
		self.product_groups = product_grouper.group_product_by_promotion(webapp_user.member, self.products)

		self.purchase_info = purchase_info

	def validate(self):
		"""判断订单是否有效

		@return True, None: 订单有效；False, reason: 订单无效, 无效原因
		"""
		order_checker = OrderChecker(self.context['webapp_owner'], self.context['webapp_user'], self)
		return order_checker.check()

	def __create_order_id(self):
		"""创建订单id

		目前采用基于时间戳＋随机数的算法生成订单id，在确定id可使用之前，通过查询mall_order表里是否有相同id来判断是否可以使用id
		这种方式比较低效，同时存在id重复的潜在隐患，后续需要改进
		"""
		#TODO2: 使用uuid替换这里的算法
		order_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
		order_id = '%s%03d' % (order_id, random.randint(1, 999))
		if mall_models.Order.select().dj_where(order_id=order_id).count() > 0:
			return self.__create_order_id()
		else:
			return order_id

	def save(self):
		"""保存订单
		"""
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']
		member = webapp_user.member

		order = mall_models.Order()
		order_business_object = Order.empty_order()

		purchase_info = self.purchase_info
		ship_info = purchase_info.ship_info
		order.ship_name = ship_info['name']
		order.ship_address = ship_info['address']
		order.ship_tel = ship_info['tel']
		order.area = ship_info['area']

		order.customer_message = purchase_info.customer_message
		order.type = purchase_info.order_type
		order.pay_interface_type = purchase_info.used_pay_interface_type
		order_business_object.pay_interface_type = order.pay_interface_type

		order.order_id = self.__create_order_id()
		order_business_object.order_id = order.order_id
		order.webapp_id = webapp_owner.webapp_id
		order.webapp_user_id = webapp_user.id
		order.member_grade_id = member.grade_id
		_, order.member_grade_discount = member.discount

		order.buyer_name = member.username_for_html

		products = self.products
		product_groups = self.product_groups

		#处理订单中的product总价
		order.product_price = sum([product.price * product.purchase_count for product in products])
		order.final_price = order.product_price
		#mall_signals.pre_save_order.send(sender=mall_signals, pre_order=fake_order, order=order, products=products, product_groups=product_groups, owner_id=request.webapp_owner_id)
		
		#积分抵扣TODO-bert IntegralAllocator
		order = self.user_integral(order)

		order.final_price = round(order.final_price, 2)
		if order.final_price < 0:
			order.final_price = 0

		#处理订单中的促销优惠金额
		promotion_saved_money = 0.0
		for product_group in product_groups:
			promotion_result = product_group.promotion_result
			if promotion_result:
				saved_money = promotion_result.get('promotion_saved_money', 0.0)
				promotion_saved_money += saved_money
		order.promotion_saved_money = promotion_saved_money

		##处理订单中的积分金额

		"""
		# 订单来自商铺
		if products[0].owner_id == webapp_owner_id:
			order.webapp_source_id = webapp_id
			order.order_source = ORDER_SOURCE_OWN
		# 订单来自微众商城
		else:
			order.webapp_source_id = WebApp.objects.get(owner_id=products[0].owner_id).appid
			order.order_source = ORDER_SOURCE_WEISHOP
		"""
		order.save()

		#更新库存
		for product in products:
			product.consume_stocks()

		#删除购物车
		if purchase_info.is_purchase_from_shopping_cart:
			for product in products:
				webapp_user.shopping_cart.remove_product(product)

		#建立<order, product>的关系
		supplier_ids = []
		for product in products:
			supplier = product.supplier
			if not supplier in supplier_ids:
				supplier_ids.append(supplier)

			mall_models.OrderHasProduct.create(
				order = order,
				product = product.id,
				product_name = product.name,
				product_model_name = product.model_name,
				number = product.purchase_count,
				total_price = product.total_price,
				price = product.price,
				promotion_id = product.used_promotion_id,
				promotion_money = product.promotion_money,
				grade_discounted_money=product.discount_money
			)

		if len(supplier_ids) > 1:
			# 进行拆单，生成子订单
			order.origin_order_id = -1 # 标记有子订单
			for supplier in supplier_ids:
				new_order = copy.copy(order)
				new_order.id = None
				new_order.order_id = '%s^%s' % (order.order_id, supplier)
				new_order.origin_order_id = order.id
				new_order.supplier = supplier
				new_order.save()
		elif supplier_ids[0] != 0:
			order.supplier = supplier_ids[0]
		order.save()
		webapp_user.use_integral(order.integral)
		#建立<order, promotion>的关系
		for product_group in product_groups:
			promotion_result = product_group.promotion_result
			if promotion_result or product_group.integral_sale_rule:
				try:
					promotion_id = product_group.promotion['id']
					promotion_type = product_group.promotion_type
				except:
					promotion_id = 0
					promotion_type = 'integral_sale'
				try:
					if not promotion_result:
						promotion_result = dict()
					promotion_result['integral_product_info'] = product_group.integral_sale_rule['integral_product_info']
				except:
					pass
				integral_money = 0
				integral_count = 0
				if product_group.integral_sale_rule and product_group.integral_sale_rule.get('result'):
					integral_money = product_group.integral_sale_rule['result']['final_saved_money']
					integral_count = product_group.integral_sale_rule['result']['use_integral']
				OrderHasPromotion.objects.create(
					order=order,
					webapp_user_id=webapp_user.id,
					promotion_id=promotion_id,
					promotion_type=promotion_type,
					promotion_result_json=json.dumps(promotion_result),
					integral_money=integral_money,
					integral_count=integral_count,
				)

		if order.final_price == 0:
			# 优惠券或积分金额直接可支付完成，直接调用pay_order，完成支付
			self.pay_order(order.order_id, True, PAY_INTERFACE_PREFERENCE)
			# 支付后的操作
			#mall_signals.post_pay_order.send(sender=Order, order=order, request=request)

		order_business_object.final_price = order.final_price
		order_business_object.id = order.id
		return order_business_object

	def user_integral(self, order):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		count_per_yuan = webapp_owner.integral_strategy_settings.integral_each_yuan

		if self.purchase_info.purchase_integral_info:
			total_integral = self.purchase_info.purchase_integral_info['integral']
			order.integral = total_integral
			order.integral_money = round(float(self.purchase_info.purchase_integral_info['money']), 2)
			order.final_price = order.final_price - order.integral_money
		return order
			
	# 	elif self.purchase_info.purchase_group2integral_info:
	# 		purchase_group2integral_info =  self.purchase_info.purchase_group2integral_info
	# 		group2integral_sale_rule = dict((group['uid'], group['integral_sale_rule']) for group in self.order.product_groups)
	# 		uid2group = dict((group['uid'], group) for group in product_groups)
	# 		for group_uid, integral_info in purchase_group2integral_info.items():
	# 			products = uid2group[group_uid]['products']
	# 			if not group_uid in group2integral_sale_rule.keys() or not group2integral_sale_rule[group_uid]:
	# 				for product in products:
	# 					fail_msg['data']['detail'].append({
	# 						'id': product.id,
	# 						'model_name': product.model_name,
	# 						'msg': '积分折扣已经过期',
	# 						'short_msg': '已经过期'
	# 					})
	# 				continue
	# 			use_integral = int(integral_info['integral'])
	# 			# integral_info['money'] = integral_info['money'] *
	# 			integral_money = round(float(integral_info['money']), 2) #round(1.0 * use_integral / count_per_yuan, 2)
				
	# 			# 校验前台输入：积分金额不能大于使用上限、积分值不能小于积分金额对应积分值
	# 			# 根据用户会员与否返回对应的商品价格
	# 			product_price = sum([product.price * product.purchase_count for product in products])
	# 			integral_sale_rule = group2integral_sale_rule[group_uid]
	# 			max_integral_price = round(product_price * integral_sale_rule['rule']['discount'] / 100, 2)
	# 			if max_integral_price < (integral_money - 0.01) \
	# 				or (integral_money * count_per_yuan) > (use_integral + 1):
	# 				for product in products:
	# 					fail_msg['data']['detail'].append({
	# 							'id': product.id,
	# 							'model_name': product.model_name,
	# 							'msg': '使用积分不能大于促销限额',
	# 							'short_msg': '积分应用',
	# 						})
	# 			integral_sale_rule = group2integral_sale_rule[group_uid]
	# 			integral_sale_rule['result'] = {
	# 				'final_saved_money': integral_money,
	# 				'promotion_saved_money': integral_money,
	# 				'use_integral': use_integral
	# 			}
	# 			total_integral += use_integral

	# 