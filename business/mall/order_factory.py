# -*- coding: utf-8 -*-
"""@package business.mall.order_factory
订单生成器

订单生成器根据购买信息(PurchaseInfo对象)，生成一个订单
"""

import json
from bs4 import BeautifulSoup
import math
import itertools
import uuid
import time
import random

from business.mall.CalculatePriceService.calculate_price_service import CalculatePriceService
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
from business.mall.reserved_product_repository import ReservedProductRepository
from business.mall.allocator.allocate_order_resource_service import AllocateOrderResourceService

class OrderException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


class OrderFactory(business_model.Model):
	"""订单生成器
	"""
	__slots__ = (
		'purchase_info',
		'products',
		'product_groups',
		'order',
		'resources',
		'price_info'
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def get(args):
		"""工厂方法，创建Order对象

		@return Order对象
		"""
		order_factory = OrderFactory(args['webapp_owner'], args['webapp_user'])
		
		return order_factory

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

	# def validate(self):
	# 	"""判断订单是否有效

	# 	@return True, None: 订单有效；False, reason: 订单无效, 无效原因
	# 	"""
	# 	order_checker = OrderChecker(self.context['webapp_owner'], self.context['webapp_user'], self)
		
	# 	return order_checker.check()

	def resource_allocator(self):
		"""资源分配器
		@return True, order: 订单有效；False, reason: 订单无效, 无效原因
		"""
		allocator_order_resource_service = AllocateOrderResourceService(self.context['webapp_owner'], self.context['webapp_user'])
		
		successed, reasons, resources = allocator_order_resource_service.allocate_resource_for(self, self.purchase_info)
		
		if successed:
			self.context['allocator_order_resource_service'] = allocator_order_resource_service
			self.resources = resources
			# #临时方案：TODO使用pricesevice处理
			# for resource in resources:
			# 	if resource.get_type() == business_model.RESOURCE_TYPE_INTEGRAL:
			# 		self.__process_order_integral_for(resource)
		else:
			allocator_order_resource_service.release(resources)
			raise OrderException(reasons)	

	# def __process_order_integral_for(self, resource):
	# 	self.order.integral = resource.integral
	# 	self.order.integral_money = resource.integral_money

	def calculate_price(self):
		calculate_price_service = CalculatePriceService(self.context['webapp_owner'], self.context['webapp_user'])
		self.price_info  = calculate_price_service.calculate_price(self, self.resources)


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

	def create_order(self, purchase_info):
		#获取订单商品集合
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		#获得已预订商品集合
		reserved_product_repository = ReservedProductRepository.get({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user
		})
		self.products = reserved_product_repository.get_reserved_products_from_purchase_info(purchase_info)
		
		#按促销进行product分组
		product_grouper = ProductGrouper()
		self.product_groups = product_grouper.group_product_by_promotion(webapp_user.member, self.products)

		#对每一个group应用促销活动
		for promotion_product_group in self.product_groups:
			promotion_product_group.apply_promotion(purchase_info)

		self.purchase_info = purchase_info
		self.order = mall_models.Order()
		self.order.products = self.products

		self.resource_allocator()
		self.calculate_price()
		#try:
		return self.save()
		# except:
		# 	self.release()
		# 	#TODO 修改提示
		# 	raise OrderException(u'保存订单失败')

	def release(self):
		allocator_order_resource_service = self.context['allocator_order_resource_service'] 
		if isinstance(allocator_order_resource_service, AllocateOrderResourceService):
			allocator_order_resource_service.release()

	def save(self):
		"""保存订单
		"""
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']
		member = webapp_user.member

		order = self.order
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

		#处理订单中的product价格信息
		order.product_price = self.price_info.get('product_price', 0)
		order.coupon_money = self.price_info.get('coupon', 0)
		order.integral_money = self.price_info.get('integral', 0)
		order.integral = self.price_info.get('integral_count', 0)
		order.final_price = self.price_info.get('final_price', 0)
		order.postage = self.price_info.get('postage', 0)

		#处理订单中的促销优惠金额
		promotion_saved_money = 0.0
		for product_group in product_groups:
			promotion_result = product_group.promotion_result
			if promotion_result:
				saved_money = promotion_result.get('saved_money', 0.0)
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

			print '-$-' * 20
			print product.price
			print product.context['is_disable_discount']
			print product.discount_money
			print id(product)
			print '-$-' * 20
			mall_models.OrderHasProduct.create(
				order = order,
				product = product.id,
				product_name = product.name,
				product_model_name = product.model_name,
				number = product.purchase_count,
				total_price = product.total_price,
				price = product.price,
				promotion_id = product.used_promotion_id,
				promotion_money = product.promotion_saved_money,
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
			if product_group.promotion:
				promotion = product_group.promotion
				promotion_result = product_group.promotion_result
				integral_money = 0
				integral_count = 0
				if promotion.type_name == 'integral_sale':
					integral_money = promotion_result['integral_money']
					integral_count = promotion_result['use_integral']
				mall_models.OrderHasPromotion.create(
					order = order,
					webapp_user_id = webapp_user.id,
					promotion_id = promotion.id,
					promotion_type = promotion.type_name,
					promotion_result_json = json.dumps(promotion_result),
					integral_money = integral_money,
					integral_count = integral_count,
				)

		if order.final_price == 0:
			# 优惠券或积分金额直接可支付完成，直接调用pay_order，完成支付
			pass
			#self.pay_order(order.order_id, True, PAY_INTERFACE_PREFERENCE)
			# 支付后的操作
			#mall_signals.post_pay_order.send(sender=Order, order=order, request=request)

		order_business_object.final_price = order.final_price
		order_business_object.id = order.id
		return order_business_object

