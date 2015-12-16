# -*- coding: utf-8 -*-
"""@package business.mall.package_order_service.package_order_service
组装资源创建订单的service

内部实现以下几步：

	* 计算订单价格，填充订单信息
	* 申请订单价相关资源
	* 调整订单价格，填充订单信息
"""

#import time
#import random
#from db.mall import models as mall_models
from business import model as business_model
from business.resource.coupon_resource import CouponResource
from business.resource.integral_resource import IntegralResource
from business.mall import postage_calculator
#from business.mall.order import Order as BussinessOrder
import logging

class PackageOrderService(business_model.Service):
	"""
	组装资源生成订单的service
	"""

	price_resources = [IntegralResource, CouponResource]

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user


	def __process_coupon(self, order, final_price):
		"""
		处理优惠券

		@return final_price 调整后的订单价格
		"""
		coupon_resource = self.type2resource.get('coupon')
		if coupon_resource:
			#order.db_model.coupon_id = coupon_resource.coupon.id
			order.coupon_id = coupon_resource.coupon.id

			forbidden_coupon_product_price = sum([product.price * product.purchase_count for product in order.products if not product.can_use_coupon])
			final_price -= forbidden_coupon_product_price
			# 优惠券面额
			coupon_denomination = coupon_resource.money
			if final_price < coupon_denomination:
				#order.db_model.coupon_money = final_price
				order.coupon_money = final_price
				final_price = 0
			else:
				#order.db_model.coupon_money = coupon_denomination
				order.coupon_money = coupon_denomination
				final_price -= coupon_denomination
			final_price += forbidden_coupon_product_price
		logging.info("`final_price` in __process_coupon(): {}".format(final_price))
		return final_price


	def __process_integral(self, order, final_price):
		"""
		处理积分

		@return final_price 调整后的订单价格
		"""
		integral_resource = self.type2resource.get('integral')
		webapp_owner = self.context['webapp_owner']

		if integral_resource:
			#order.db_model.integral = integral_resource.integral
			#order.db_model.integral_money = integral_resource.money
			#order.db_model.integral_each_yuan = webapp_owner.integral_strategy_settings.integral_each_yuan
			order.integral = integral_resource.integral
			order.integral_money = integral_resource.money
			order.integral_each_yuan = webapp_owner.integral_strategy_settings.integral_each_yuan
			final_price -= integral_resource.money
		logging.info("`final_price` in __process_integral(): {}".format(final_price))
		return final_price


	def __process_postage(self, order, final_price, purchase_info):
		"""
		处理运费

		@return final_price 调整后的订单价格
		"""
		postage_config = self.context['webapp_owner'].system_postage_config
		calculator = postage_calculator.PostageCalculator(postage_config)
		postage = calculator.get_postage(order.products, purchase_info)
		#order.db_model.postage = postage
		order.postage = postage
		final_price += postage
		logging.info("`final_price` in __process_postage(): {}".format(final_price))
		return final_price


	def __process_promotion(self, order):
		"""
		处理促销

		"""
		promotion_saved_money = 0.0
		for product_group in order.product_groups:
			promotion_result = product_group.promotion_result
			if promotion_result:
				saved_money = promotion_result.saved_money
				promotion_saved_money += saved_money
		order.promotion_saved_money = promotion_saved_money
		return


	def __allocate_price_related_resource(self, order, purchase_info):
		"""
		分配订单价格相关的资源

		@todo 待实现
		"""
		return []


	def __adjust_order_price(self, order, price_related_resources, purchase_info):
		"""
		再次调整订单价格（比如微众卡支付过后调整）
		"""
		return order


	def package_order(self, order, price_free_resources, purchase_info):
		"""
		组装订单

		@param resources 表示与订单价格无关的资源

		@return order 订单对象(业务层)
		@return price_related_resources
		"""


		# 读取resources中的信息
		# TODO: 如果有多个resource有同一个type呢？
		self.type2resource = dict([(resource.type, resource) for resource in price_free_resources])

		# 处理通用券 todo 适配单品券
		final_price = sum([product.price * product.purchase_count for product in order.products])

		# 处理优惠券
		final_price = self.__process_coupon(order, final_price)

		# 处理积分
		# TODO: 确认积分应用
		final_price = self.__process_integral(order, final_price)

		# 处理运费
		final_price = self.__process_postage(order, final_price, purchase_info)

		# 处理订单中的促销优惠金额
		self.__process_promotion(order)

		# todo 确认字段是否遗漏
		logging.info("final_price={}".format(final_price))
		if final_price < 0:
			logging.error('`final_price` SHOULD NOT be negative! Please check it.')
			final_price = 0
		order.final_price = round(final_price, 2)

		# TODO: 需要实现"订单价格相关资源"分配
		price_related_resources = self.__allocate_price_related_resource(order, purchase_info)

		# 根据订单价格相关资源调整待支付价格
		# TODO: 处理微众卡
		order = self.__adjust_order_price(order, price_related_resources, purchase_info)

		order.final_price = round(order.final_price, 2)
		logging.info("order.final_price={}".format(order.final_price))
		return order, price_related_resources
