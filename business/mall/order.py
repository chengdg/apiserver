# -*- coding: utf-8 -*-

"""订单商品

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
from cache import utils as cache_util
from wapi.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.mall.order_products import OrderProducts
from business.mall.product_grouper import ProductGrouper
from business.mall.order_checker import OrderChecker


class Order(business_model.Model):
	"""用于支持购买过程中进行订单编辑的订单
	"""
	__slots__ = (
		'id',
		'order_id',
		'type',
		'purchase_info',
		'ship_info',
		'products',
		'postage',
		'product_groups',
		'pay_interfaces',
		'usable_integral',
		'final_price'
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'purchase_info'])
	def create(args):
		"""工厂方法，创建Order对象

		@return Order对象
		"""
		order = Order(args['webapp_owner'], args['webapp_user'], args['purchase_info'])

		return order

	def __init__(self, webapp_owner, webapp_user, purchase_info):
		business_model.Model.__init__(self)

		self.context['purchase_info'] = purchase_info
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
		#TODO2: 使用uuid替换这里的算法
		order_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
		order_id = '%s%03d' % (order_id, random.randint(1, 999))
		if mall_models.Order.select().dj_where(order_id=order_id).count() > 0:
			return self.__create_order_id()
		else:
			return order_id

	def pay(self, order_id, is_success, pay_interface_type):
		"""支付订单
		"""
		pass
		try:
			order = get_order(webapp_user, order_id, is_need_area=False)
		except:
			watchdog_fatal(u"本地获取订单信息失败：order_id:{}, cause:\n{}".format(order_id, unicode_full_stack()))
			return None, False

		pay_result = False

		if is_success and order.status == ORDER_STATUS_NOT: #支付成功
			pay_result = True

			# jz 2015-10-20
			# Order.objects.filter(order_id=order_id).update(status=ORDER_STATUS_PAYED_NOT_SHIP, pay_interface_type=pay_interface_type, payment_time=datetime.now())
			#order.status = ORDER_STATUS_PAYED_SUCCESSED
			#order.status = ORDER_STATUS_PAYED_NOT_SHIP
			# 修改子订单的订单状态，该处有逻辑状态的校验
			# origin_order_id = Order.objects.get(order_id=order_id).id
			# Order.objects.filter()
			if order.origin_order_id < 0:
				Order.objects.filter(origin_order_id=order.id).update(status=ORDER_STATUS_PAYED_NOT_SHIP, pay_interface_type=pay_interface_type, payment_time=datetime.now())

			order.status = ORDER_STATUS_PAYED_NOT_SHIP
			order.pay_interface_type = pay_interface_type
			order.payment_time = datetime.now()
			order.save()

			#记录日志
			record_operation_log(order_id, u'客户', u'支付')
			record_status_log(order_id, u'客户', ORDER_STATUS_NOT, ORDER_STATUS_PAYED_NOT_SHIP)
			# jz 2015-10-20
			#记录购买统计项
			# PurchaseDailyStatistics.objects.create(
			# 	webapp_id = webapp_id,
			# 	webapp_user_id = webapp_user.id,
			# 	order_id = order_id,
			# 	order_price = order.final_price,
			# 	date = dateutil.get_today()
			# )

			#更新webapp_user的has_purchased字段
			webapp_user.set_purchased()

			try:
				mall_util.email_order(order=order)
			except:
				notify_message = u"订单状态为已付款时发邮件失败，order_id={}, webapp_id={}, cause:\n{}".format(order_id, webapp_id, unicode_full_stack())
				watchdog_alert(notify_message)
			# 重新查询订单
			# order = get_order(webapp_user, order_id, True)
		return order, pay_result

	def save(self):
		"""保存订单
		"""
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']
		member = webapp_user.member

		order = mall_models.Order()

		purchase_info = self.context['purchase_info']
		ship_info = purchase_info.ship_info
		order.ship_name = ship_info['name']
		order.ship_address = ship_info['address']
		order.ship_tel = ship_info['tel']
		order.area = ship_info['area']

		order.customer_message = purchase_info.customer_message
		order.type = purchase_info.order_type
		order.pay_interface_type = purchase_info.used_pay_interface_type

		order.order_id = self.__create_order_id()
		self.order_id = order.order_id
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
		order.final_price = round(order.final_price, 2)
		if order.final_price < 0:
			order.final_price = 0

		#处理订单中的促销优惠金额
		promotion_saved_money = 0.0
		for product_group in product_groups:
			promotion_result = product_group['promotion_result']
			if promotion_result:
				saved_money = promotion_result.get('promotion_saved_money', 0.0)
				promotion_saved_money += saved_money
		order.promotion_saved_money = promotion_saved_money

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

		#建立<order, promotion>的关系
		for product_group in product_groups:
			promotion_result = product_group.get('promotion_result', None)
			if promotion_result or product_group.get('integral_sale_rule', None):
				try:
					promotion_id = product_group['promotion']['id']
					promotion_type = product_group['promotion_type']
				except:
					promotion_id = 0
					promotion_type = 'integral_sale'
				try:
					if not promotion_result:
						promotion_result = dict()
					promotion_result['integral_product_info'] = product_group['integral_sale_rule']['integral_product_info']
				except:
					pass
				integral_money = 0
				integral_count = 0
				if product_group['integral_sale_rule'] and product_group['integral_sale_rule'].get('result'):
					integral_money = product_group['integral_sale_rule']['result']['final_saved_money']
					integral_count = product_group['integral_sale_rule']['result']['use_integral']
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

		self.final_price = order.final_price
		return True