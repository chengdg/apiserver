# -*- coding: utf-8 -*-


from business import model as business_model
from business.resource.coupon_resource import CouponResource
from business.resource.integral_resource import IntegralResource
from business.mall import postage_calculator


class CalculatePriceService(business_model.Service):
	"""
	CalculatePriceService
	"""

	price_resources = [IntegralResource, CouponResource]

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		self.context['price_info'] = []

	def calculate_price(self, order, resources):
		# 最终总金额final_price = (product_price + postage) - (coupon_money + integral_money + weizoom_card_money + promotion_saved_money + edit_money)

		order_price_info = dict([(resource.type, resource.money) for resource in resources if type(resource) in CalculatePriceService.price_resources and getattr(resource, resource.type)])

		products = order.products

		# 处理商品购买价
		order_price_info['product_price'] = sum([product.price * product.purchase_count for product in products])
		# 处理邮费
		postage_config = self.context['webapp_owner'].system_postage_config
		calculator = postage_calculator.PostageCalculator(postage_config)
		postage = calculator.get_postage(order)
		order_price_info['postage'] = postage

		final_price = order_price_info['product_price']
		# 优惠券面额
		coupon_denomination = order_price_info.get('coupon', 0)
		if final_price < coupon_denomination:
			order_price_info['coupon'] = final_price
			final_price = 0
		else:
			final_price -= coupon_denomination

		# 处理积分抵扣金额
		final_price -= order_price_info.get('integral', 0)
		#邮费
		final_price += order_price_info.get('postage', 0)
		# 处理微众卡
		final_price -= order_price_info.get('weizoom_card', 0)
		# todo 处理promotion_saved_money

		if final_price < 0:
			final_price = 0

		order_price_info['final_price'] = round(final_price, 2)

		type2resource = dict([(resource.type, resource) for resource in resources if type(resource) in CalculatePriceService.price_resources and getattr(resource, resource.type)])

		#add by bert 临时解决方案 
		if order_price_info.get('integral', 0):
			order_price_info['integral_count'] = type2resource.get('integral').integral


		return order_price_info