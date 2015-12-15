# -*- coding: utf-8 -*-
import time
import random
from db.mall import models as mall_models
from business import model as business_model
from business.resource.coupon_resource import CouponResource
from business.resource.integral_resource import IntegralResource
from business.mall import postage_calculator
from business.mall.order import Order as BussinessOrder


class PackageOrderService(business_model.Service):
	"""
	CalculatePriceService
	"""

	price_resources = [IntegralResource, CouponResource]

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user


	def package_order(self, order_factory, resources, purchase_info):
		order = BussinessOrder.empty_order()

		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']
		member = webapp_user.member

		# 读取基本信息
		order.webapp_id = webapp_owner.webapp_id
		order.webapp_user_id = webapp_user.id
		order.member_grade_id = member.grade_id
		order.member_grade_discount = member.discount
		order.buyer_name = member.username_for_html

		# 读取purchase_info信息
		ship_info = purchase_info.ship_info
		order.ship_name = ship_info['name']
		order.ship_address = ship_info['address']
		order.ship_tel = ship_info['tel']
		order.area = ship_info['area']
		order.customer_message = purchase_info.customer_message
		order.type = purchase_info.order_type
		order.pay_interface_type = purchase_info.used_pay_interface_type

		type2resource = dict([(resource.type, resource) for resource in resources])

		# 读取resources中的信息
		# 处理通用券 todo 适配单品券
		final_price = sum([product.price * product.purchase_count for product in order_factory.products])

		if type2resource.get('coupon', None):
			coupon_resource = type2resource['']
			order.coupon_id = coupon_resource.coupon.id

			forbidden_coupon_product_price = sum([product.price * product.purchase_count for product in order_factory.products if not product.can_use_coupon])
			final_price -= forbidden_coupon_product_price
			# 优惠券面额
			coupon_denomination = coupon_resource.money
			if final_price < coupon_denomination:
				order.coupon_money = final_price
				final_price = 0
			else:
				order.coupon_money = coupon_denomination
				final_price -= coupon_denomination
			final_price += forbidden_coupon_product_price

		# 处理积分 todo 确认积分应用
		if type2resource.get('integral', 0):
			integral_resource = type2resource['integral']
			order.integral = integral_resource.integral
			order.integral_money = integral_resource.money
			order.integral_each_yuan = webapp_owner.integral_strategy_settings.integral_each_yuan
			final_price -= integral_resource.money

		# 处理邮费
		postage_config = self.context['webapp_owner'].system_postage_config
		calculator = postage_calculator.PostageCalculator(postage_config)
		postage = calculator.get_postage(order_factory)
		order.postage = postage
		final_price += postage

		# 处理订单中的促销优惠金额
		promotion_saved_money = 0.0
		for product_group in order_factory.product_groups:
			promotion_result = product_group.promotion_result
			if promotion_result:
				saved_money = promotion_result.saved_money
				promotion_saved_money += saved_money
		order.promotion_saved_money = promotion_saved_money

		# todo 确认字段是否遗漏

		# todo 处理微众卡

		if final_price < 0:
			final_price = 0

		order.final_price = round(final_price, 2)
		return order





	# 读取resource中相关价格信息，计算并填充


	def __create_order_id(self):
		"""创建订单id

		目前采用基于时间戳＋随机数的算法生成订单id，在确定id可使用之前，通过查询mall_order表里是否有相同id来判断是否可以使用id
		这种方式比较低效，同时存在id重复的潜在隐患，后续需要改进
		"""
		# TODO2: 使用uuid替换这里的算法
		order_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
		order_id = '%s%03d' % (order_id, random.randint(1, 999))
		if mall_models.Order.select().dj_where(order_id=order_id).count() > 0:
			return self.__create_order_id()
		else:
			return order_id
