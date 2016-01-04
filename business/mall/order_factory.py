# -*- coding: utf-8 -*-
"""@package business.mall.order_factory
订单生成器

@brief 订单生成器根据购买信息(PurchaseInfo对象)，生成一个订单。


下单步骤
-----------------

1. 申请订单价无关资源（比如：reserved product, coupon, integral）
2. 计算订单价格（填充资源信息到订单业务对象中）
3. 申请订单价相关资源（比如：微众卡）
4. 调整订单价格（填充资源信息到订单业务对象中）
5. 保存订单
6. 如果需要（比如订单保存失败），释放资源（包括订单价相关资源和订单价无关资源）

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
#import resource
from core.watchdog.utils import watchdog_alert,watchdog_error
from core.exceptionutil import unicode_full_stack
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
from business.mall.order_exception import OrderException


class OrderFactory(business_model.Model):
	"""
	订单生成器
	"""
	__slots__ = (
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

	def __allocate_price_free_resources(self, order, purchase_info):
		"""
		申请订单价无关资源

		说明：`reason`的格式

 			{
				"is_success": False,
				"type": 'promotion:expired',
				"msg": u"该活动已经过期",
				"short_msg": u"已经过期"
			}
		
		@see __allocation_promotion()

		@return price_free_resources
		"""
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		allocate_order_resource_service = AllocateOrderResourceService(webapp_owner, webapp_user)
		
		successed, reasons, resources = allocate_order_resource_service.allocate_resource_for(order, purchase_info)
		
		if successed:
			logging.info(u"Allocated resources successfully. count: {}".format(len(resources)))

			self.context['allocator_order_resource_service'] = allocate_order_resource_service
			#self.resources = resources
			# #临时方案：TODO使用pricesevice处理
			# for resource in resources:
			# 	if resource.get_type() == business_model.RESOURCE_TYPE_INTEGRAL:
			# 		self.__process_order_integral_for(resource)
			return resources
		else:
			# 如果分配资源失败，则抛异常
			logging.info(u"count of `reasons`: {}".format(len(reasons)))
			logging.info(u"reasons in OrderFactory.create_order: ")
			for reason in reasons:
				logging.info(u"reason: name: {}, short_msg: {}".format(reason.get('name'), reason.get('short_msg')))
			allocate_order_resource_service.release(resources)
			raise OrderException(reasons)	


	def __process_products(self, order, purchase_info):
		"""
		向order中添加products和product_groups

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
		return order


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
		_, order.member_grade_discount = member.discount
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
		order.status = mall_models.ORDER_STATUS_NOT

		return order


	def release(self, resources):
		"""
		释放资源
		"""
		allocator_order_resource_service = self.context['allocator_order_resource_service'] 
		if isinstance(allocator_order_resource_service, AllocateOrderResourceService):
			allocator_order_resource_service.release(resources)


	def __save_order(self, order):
		"""
		保存订单

		@param[in] order Order对象(业务模型)
		"""
		#webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		logging.debug("order.db_model={}".format(order.db_model))
		try:
			order.save()
			if order.final_price == 0:
				# 优惠券或积分金额直接可支付完成，直接调用pay_order，完成支付
				order.pay(mall_models.PAY_INTERFACE_PREFERENCE)
				# 支付后的操作
				#mall_signals.post_pay_order.send(sender=Order, order=order, request=request)

		except:
			notify_message = u"__save_order error cause:\n{}".format(unicode_full_stack())
			logging.error(notify_message)
			watchdog_error(notify_message)
			return None

		
		return order



	def create_order(self, purchase_info):
		"""
		由PurchaseInfo创建订单

		"""
		
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		# 创建空订单
		order = Order.empty_order(webapp_owner, webapp_user)

		# 初始化，不需要资源信息
		order = self.__init_order(order, purchase_info)
		# 初始化商品信息
		order = self.__process_products(order, purchase_info)

		# 申请订单价无关资源
		price_free_resources = self.__allocate_price_free_resources(order, purchase_info)
		logging.info(u"price_free_resources={}".format(price_free_resources))

		# 填充order
		package_order_service = PackageOrderService(webapp_owner, webapp_user)
		# 如果is_success=False, 表示分配资源失败
		order, is_success, reasons = package_order_service.package_order(order, price_free_resources, purchase_info)

		if is_success: # 组装订单成功
			#如果前端提交了积分使用信息，识别哪些商品使用了积分
			if purchase_info.group2integralinfo:
				group2integralinfo = purchase_info.group2integralinfo
				for product_group in order.product_groups:
					if not product_group.uid in group2integralinfo:
						product_group.disable_integral_sale()
			else:
				for product_group in order.product_groups:
					product_group.disable_integral_sale()

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
			return order

		# 创建订单失败
		logging.error("Failed to create Order object or save the order! Release all resources. order={}".format(order))
		self.release(price_free_resources)
		# PackageOrderService分配资源失败，price_related_resources应为[]，不需要release
		raise OrderException(reasons)
