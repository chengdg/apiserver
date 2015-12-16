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
import copy
import logging

from business.mall.order import Order

#from business.mall.package_order_service.package_order_service import CalculatePriceService
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
from business.mall.group_reserved_product_service import GroupReservedProductService
from business.mall.order import Order
from business.mall.reserved_product_repository import ReservedProductRepository
from business.mall.allocator.allocate_order_resource_service import AllocateOrderResourceService
from business.mall.package_order_service.package_order_service import PackageOrderService

from business.mall.reserved_product_repository import ReservedProductRepository
from business.mall.group_reserved_product_service import GroupReservedProductService


class OrderException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)






class OrderFactory(business_model.Model):
	"""
	订单生成器
	"""
	__slots__ = (
		#'purchase_info',
		#'products',
		#'product_groups',
		#'order',
		'resources',
		'price_info'
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def get(args):
		"""
		工厂方法，创建Order对象

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


	def __create_order_id(self):
		"""创建订单id

		目前采用基于时间戳＋随机数的算法生成订单id，在确定id可使用之前，通过查询mall_order表里是否有相同id来判断是否可以使用id
		这种方式比较低效，同时存在id重复的潜在隐患，后续需要改进

		@todo 可以考虑用时间戳加MD5方式
		@bug 这里不应该暴露存储层
		"""
		# TODO2: 使用uuid替换这里的算法
		order_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
		order_id = '%s%03d' % (order_id, random.randint(1, 999))
		if mall_models.Order.select().dj_where(order_id=order_id).count() > 0:
			return self.__create_order_id()
		else:
			return order_id


	def __allocate_resource(self, order, purchase_info):
		"""
		分配订单资源

		@return True, order: 订单有效；False, reason: 订单无效, 无效原因
		"""
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		allocate_order_resource_service = AllocateOrderResourceService(webapp_owner, webapp_user)
		
		successed, reasons, resources = allocate_order_resource_service.allocate_resource_for(order, purchase_info)
		
		if successed:
			logging.info("Allocated resources successfully. count: {}".format(len(resources)))

			self.context['allocator_order_resource_service'] = allocate_order_resource_service
			self.resources = resources
			# #临时方案：TODO使用pricesevice处理
			# for resource in resources:
			# 	if resource.get_type() == business_model.RESOURCE_TYPE_INTEGRAL:
			# 		self.__process_order_integral_for(resource)
			return resources
		else:
			allocate_order_resource_service.release(resources)
			raise OrderException(reasons)	


	def __process_products(self, order, purchase_info):
		"""
		@note 从OrderFactory迁移的代码
		"""
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		#获得已预订商品集合
		reserved_product_repository = ReservedProductRepository.get({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user
		})
		order.products = reserved_product_repository.get_reserved_products_from_purchase_info(purchase_info)

		#按促销进行product分组
		group_reserved_product_service = GroupReservedProductService.get(webapp_owner, webapp_user)
		order.product_groups = group_reserved_product_service.group_product_by_promotion(order.products)

		#对每一个group应用促销活动
		for promotion_product_group in order.product_groups:
			promotion_product_group.apply_promotion(purchase_info)

		return
	# def __process_order_integral_for(self, resource):
	# 	self.order.integral = resource.integral
	# 	self.order.integral_money = resource.integral_money


	'''
	def _package_order(self):
		"""
		计算订单价格
		"""
		package_order_service = CalculatePriceService.get(self.context['webapp_owner'], self.context['webapp_user'])
		self.order = package_order_service.package_order(self, self.resources.self.purchase)
	'''


	def __init_order(self, order, purchase_info):
		"""
		初始化订单对象
		"""
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']
		member = webapp_user.member

		# 读取基本信息
		order.webapp_id = webapp_owner.webapp_id
		order.webapp_user_id = webapp_user.id
		order.member_grade_id = member.grade_id
		#order.member_grade_discount = member.discount
		# 'member_grade_discount': '(175, 100)' ?
		order.member_grade_discount = 100 #member.discount
		order.buyer_name = member.username_for_html

		# 读取purchase_info信息
		ship_info = purchase_info.ship_info
		order.ship_name = ship_info['name']
		order.ship_address = ship_info['address']
		order.ship_tel = ship_info['tel']
		order.ship_area = ship_info['area']
		order.customer_message = purchase_info.customer_message
		order.type = purchase_info.order_type
		order.pay_interface_type = purchase_info.used_pay_interface_type
		order.order_id = self.__create_order_id()

		'''
		# 读取基本信息
		order.db_model.webapp_id = webapp_owner.webapp_id
		order.webapp_id = webapp_owner.webapp_id

		order.db_model.webapp_user_id = webapp_user.id
		order.webapp_user_id = webapp_user.id

		order.db_model.member_grade_id = member.grade_id
		order.member_grade_id = member.grade_id

		#order.db_model.member_grade_discount = member.discount
		# 'member_grade_discount': '(175, 100)' ?
		order.db_model.member_grade_discount = 100 #member.discount
		order.member_grade_discount = 100 #member.discount

		order.db_model.buyer_name = member.username_for_html
		order.buyer_name = member.username_for_html

		# 读取purchase_info信息
		ship_info = purchase_info.ship_info
		order.db_model.ship_name = ship_info['name']
		order.ship_name = ship_info['name']

		order.db_model.ship_address = ship_info['address']
		order.ship_address = ship_info['address']

		order.db_model.ship_tel = ship_info['tel']
		order.ship_tel = ship_info['tel']

		order.db_model.area = ship_info['area']
		order.ship_area = ship_info['area']

		order.db_model.customer_message = purchase_info.customer_message
		order.customer_message = purchase_info.customer_message

		order.db_model.type = purchase_info.order_type
		order.type = purchase_info.order_type

		order.db_model.pay_interface_type = purchase_info.used_pay_interface_type
		order.pay_interface_type = purchase_info.used_pay_interface_type

		order.db_model.order_id = self.__create_order_id()
		'''
		return


	def __allocate_price_free_resources(self, order, purchase_info):
		"""
		申请订单价无关资源

		@return price_free_resources
		"""
		
		# 分配订单资源
		price_free_resources = self.__allocate_resource(order, purchase_info)
		# TODO: to be implemented
		return price_free_resources



	'''
	def create_order_old(self, purchase_info):
		"""
		由PurchaseInfo创建订单
		"""
		#获取订单商品集合
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		# 改到PackageOrderService中
		"""
		#获得已预订商品集合
		reserved_product_repository = ReservedProductRepository.get({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user
		})
		self.products = reserved_product_repository.get_reserved_products_from_purchase_info(purchase_info)
		
		#按促销进行product分组
		group_reserved_product_service = GroupReservedProductService.get(webapp_owner, webapp_user)
		self.product_groups = group_reserved_product_service.group_product_by_promotion(self.products)

		#对每一个group应用促销活动
		for promotion_product_group in self.product_groups:
			promotion_product_group.apply_promotion(purchase_info)

		self.purchase_info = purchase_info
		"""

		# 分配订单资源
		self._allocate_resource()
		# 组装订单
		self._package_order()
		#try:
		return self.save()
		# except:
		# 	self.release()
		# 	#TODO 修改提示
		# 	raise OrderException(u'保存订单失败')
	'''

	def release(self):
		allocator_order_resource_service = self.context['allocator_order_resource_service'] 
		if isinstance(allocator_order_resource_service, AllocateOrderResourceService):
			allocator_order_resource_service.release()


	def __save_order(self, order):
		"""
		保存订单

		@param order Order对象(业务模型)
		"""
		#webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		#order = self.order

		products = order.products
		product_groups = order.product_groups

		logging.info("order.db_model={}".format(order.db_model))
		order.save()
		#order.db_model.save()

		#建立<order, product>的关系
		supplier_ids = []
		for product in products:
			supplier = product.supplier
			if not supplier in supplier_ids:
				supplier_ids.append(supplier)

			mall_models.OrderHasProduct.create(
				order = order.db_model,
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
			order.db_model.origin_order_id = -1 # 标记有子订单
			for supplier in supplier_ids:
				new_order = copy.deepcopy(order.db_model)
				new_order.id = None
				new_order.order_id = '%s^%s' % (order.order_id, supplier)
				new_order.origin_order_id = order.id
				new_order.supplier = supplier
				new_order.save()
		elif supplier_ids[0] != 0:
			order.db_model.supplier = supplier_ids[0]
		order.save()
		#order.db_model.save()

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
					order = order.db_model,
					webapp_user_id = webapp_user.id,
					promotion_id = promotion.id,
					promotion_type = promotion.type_name,
					promotion_result_json = json.dumps(promotion_result.to_dict()),
					integral_money = integral_money,
					integral_count = integral_count,
				)

		if order.final_price == 0:
			# 优惠券或积分金额直接可支付完成，直接调用pay_order，完成支付
			pass
			#self.pay_order(order.order_id, True, PAY_INTERFACE_PREFERENCE)
			# 支付后的操作
			#mall_signals.post_pay_order.send(sender=Order, order=order, request=request)

		#order_business_object = Order.empty_order()
		#order_business_object.pay_interface_type = order.pay_interface_type
		#order_business_object.order_id = order.order_id
		#order_business_object.final_price = order.final_price
		#order_business_object.id = order.id
		#return order_business_object
		return order



	def create_order(self, purchase_info):
		"""
		由PurchaseInfo创建订单

		**下单步骤**：
			1. 申请订单价无关资源（比如：reserved product, coupon, integral）
			2. 计算订单价格（填充资源信息到订单业务对象中）
			3. 申请订单价相关资源（比如：微众卡）
			4. 调整订单价格（填充资源信息到订单业务对象中）
			5. 保存订单
			6. 如果需要（比如订单保存失败），释放资源（包括订单价相关资源和订单价无关资源）
		"""
		
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		order = Order.empty_order()

		# 初始化，不需要资源信息
		self.__init_order(order, purchase_info)
		# 初始化商品信息
		self.__process_products(order, purchase_info)
	

		# 申请订单价无关资源
		price_free_resources = self.__allocate_price_free_resources(order, purchase_info)
		logging.info("price_free_resources={}".format(price_free_resources))

		# 填充order
		package_order_service = PackageOrderService(webapp_owner, webapp_user)
		order,  price_related_resources = package_order_service.package_order(order, price_free_resources, purchase_info)

		# 保存订单
		order = self.__save_order(order)

		# 如果需要（比如订单保存失败），释放资源
		if order and order.is_saved:
			#删除购物车
			# TODO: 删除购物车不应该放在这里
			logging.warning('to clean the CART')
			if purchase_info.is_purchase_from_shopping_cart:
				for product in order.products:
					webapp_user.shopping_cart.remove_product(product)
		else:
			self.release(price_free_resources)
			self.release(price_related_resources)

		return order
